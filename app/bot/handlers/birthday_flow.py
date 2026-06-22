from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.inline import back_cancel_keyboard, preview_keyboard
from app.bot.states.birthday import BirthdayFlow
from app.config import get_settings
from app.database.models import PromptType
from app.database.repositories.posts import PostRepository
from app.database.repositories.prompts import PromptRepository
from app.services.image_generation import ImageGenerationService
from app.services.post_builder import PostBuilder
from app.services.prompt_renderer import SafePromptRenderer
from app.utils.dates import default_publication_datetime, parse_birth_date, parse_publication_datetime

router = Router()


@router.message(F.text == "Новый именинник")
async def new_person(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(BirthdayFlow.waiting_photo)
    await message.answer("Отправьте фотографию именинника.", reply_markup=back_cancel_keyboard())


@router.message(BirthdayFlow.waiting_photo)
async def receive_photo(message: Message, state: FSMContext, bot: Bot, session: AsyncSession) -> None:
    if not message.photo:
        await message.answer("Нужно отправить именно фото. Попробуйте ещё раз.")
        return
    file_id = message.photo[-1].file_id
    settings = get_settings()
    prompt_template = await PromptRepository(session).get_active(PromptType.IMAGE)
    prompt = prompt_template.content if prompt_template else ""
    rendered = SafePromptRenderer().render(
        prompt,
        {
            "full_name": "",
            "position": "",
            "branch": "",
            "birth_date": "",
            "company_style": settings.default_company_style,
            "language": "ru",
            "photo_requirements": "сохранить узнаваемость, корпоративное оформление",
        },
    )
    path, generated_file_id = await ImageGenerationService(settings).generate_from_telegram_photo(
        bot, file_id, rendered
    )
    await state.update_data(
        original_photo_file_id=file_id,
        generated_photo_path=path,
        generated_photo_file_id=generated_file_id,
    )
    await state.set_state(BirthdayFlow.waiting_full_name)
    await message.answer("Введите ФИО именинника.", reply_markup=back_cancel_keyboard())


@router.message(BirthdayFlow.waiting_full_name)
async def receive_full_name(message: Message, state: FSMContext) -> None:
    await state.update_data(full_name=message.text.strip())
    await state.set_state(BirthdayFlow.waiting_position)
    await message.answer("Введите должность.", reply_markup=back_cancel_keyboard())


@router.message(BirthdayFlow.waiting_position)
async def receive_position(message: Message, state: FSMContext) -> None:
    await state.update_data(position=message.text.strip())
    await state.set_state(BirthdayFlow.waiting_branch)
    await message.answer("Введите филиал.", reply_markup=back_cancel_keyboard())


@router.message(BirthdayFlow.waiting_branch)
async def receive_branch(message: Message, state: FSMContext) -> None:
    await state.update_data(branch=message.text.strip())
    await state.set_state(BirthdayFlow.waiting_birth_date)
    await message.answer("Введите дату рождения в формате ДД.ММ или ДД.ММ.ГГГГ.")


@router.message(BirthdayFlow.waiting_birth_date)
async def receive_birth_date(message: Message, state: FSMContext, session: AsyncSession, db_user) -> None:
    settings = get_settings()
    try:
        birth_date = parse_birth_date(message.text)
    except ValueError as exc:
        await message.answer(str(exc))
        return

    data = await state.get_data()
    publication_dt = default_publication_datetime(birth_date, settings.tz)
    person = await PostRepository(session).create_person(
        full_name=data["full_name"],
        position=data["position"],
        branch=data["branch"],
        birth_date=birth_date,
        original_photo_file_id=data["original_photo_file_id"],
        generated_photo_path=data["generated_photo_path"],
        generated_photo_file_id=data["generated_photo_file_id"],
        created_by=db_user.id,
    )
    post = await PostBuilder(session, settings).attach_person_and_refresh_text(
        person, publication_dt, db_user.id
    )
    await state.clear()
    await message.answer(
        PostBuilder.preview_text(post),
        reply_markup=preview_keyboard(post.id),
    )


@router.callback_query(F.data.startswith("post:approve:"))
async def approve_post(callback: CallbackQuery, session: AsyncSession, db_user) -> None:
    post_id = int(callback.data.rsplit(":", 1)[1])
    post = await PostRepository(session).get_post(post_id)
    if not post:
        await callback.answer("Пост не найден", show_alert=True)
        return
    await PostRepository(session).approve(post, db_user.id)
    await callback.message.edit_text(
        f"Пост подтверждён и будет опубликован {post.publication_datetime:%d.%m.%Y %H:%M}."
    )


@router.callback_query(F.data.startswith("post:cancel:"))
async def cancel_post(callback: CallbackQuery, session: AsyncSession) -> None:
    post_id = int(callback.data.rsplit(":", 1)[1])
    post = await PostRepository(session).get_post(post_id)
    if post:
        await PostRepository(session).cancel(post)
    await callback.message.edit_text("Пост отменён.")


@router.callback_query(F.data.startswith("post:text:"))
async def ask_manual_text(callback: CallbackQuery, state: FSMContext) -> None:
    post_id = int(callback.data.rsplit(":", 1)[1])
    await state.update_data(post_id=post_id)
    await state.set_state(BirthdayFlow.waiting_manual_text)
    await callback.message.answer("Отправьте новый текст поздравления.")


@router.message(BirthdayFlow.waiting_manual_text)
async def save_manual_text(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    post = await PostRepository(session).get_post(data["post_id"])
    if not post:
        await message.answer("Пост не найден.")
        await state.clear()
        return
    post.text = message.text
    post.text_is_manual = True
    await state.clear()
    await message.answer(PostBuilder.preview_text(post), reply_markup=preview_keyboard(post.id))


@router.callback_query(F.data.startswith("post:date:"))
async def ask_publication_date(callback: CallbackQuery, state: FSMContext) -> None:
    post_id = int(callback.data.rsplit(":", 1)[1])
    await state.update_data(post_id=post_id)
    await state.set_state(BirthdayFlow.waiting_publication_datetime)
    await callback.message.answer("Введите дату публикации: ДД.ММ.ГГГГ ЧЧ:ММ")


@router.message(BirthdayFlow.waiting_publication_datetime)
async def save_publication_date(message: Message, state: FSMContext, session: AsyncSession) -> None:
    settings = get_settings()
    try:
        publication_dt = parse_publication_datetime(message.text, settings.tz)
    except ValueError as exc:
        await message.answer(str(exc))
        return
    data = await state.get_data()
    post = await PostRepository(session).get_post(data["post_id"])
    if not post:
        await message.answer("Пост не найден.")
        await state.clear()
        return
    post.publication_datetime = publication_dt
    await state.clear()
    await message.answer(PostBuilder.preview_text(post), reply_markup=preview_keyboard(post.id))


@router.callback_query(F.data == "flow:cancel")
async def cancel_flow(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer("Действие отменено.")

