from loguru import logger

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.db import User, Gif, get_last_gif_id
from src.utils import AddGif, inline_builder, Reason
from src import admin

router = Router()


@router.message(Command("addgif"))
async def addgif_cmd(message: Message, state: FSMContext):
    await state.clear()
    
    await message.reply("<b>✨ Отправьте гиф, которую хотите добавить в базу:</b>")
    
    await state.set_state(AddGif.gif)


@router.message(AddGif.gif, F.animation)
async def addgif_gif(message: Message, state: FSMContext):
    await state.update_data({"gif": message.animation.file_id})

    await message.reply("<b>Отлично, теперь отправьте название. Оно не должно превышать 32 символа!</b>")
    await state.set_state(AddGif.title)


@router.message(AddGif.title, F.text)
async def addgif_title(message: Message, state: FSMContext):
    if len(message.text) > 32:
        await message.reply("<b>Название гифки не должно превышать 32 символа!</b>")
        return
    if await Gif.find_one(Gif.title == message.text):
        await message.reply("<b>Гиф с таким названием уже есть в базе!</b>")
        return
    
    await state.update_data({"title": message.text})
    await message.reply(
        "<b>Супер, теперь отправьте описание. Оно не должно превышать 256 символов. (Если не хотите, нажмите кнопку ниже)</b>",
        reply_markup=inline_builder(["пропустить", "skip"])
    )
    await state.set_state(AddGif.description)


@router.message(AddGif.description, F.text)
async def addgif_description(message: Message, state: FSMContext):
    if len(message.text) > 256:
        await message.reply("<b>Описание гифки не должно превышать 256 символов!</b>")
        return
    
    await state.update_data({"description": message.text})
    await state.set_state(AddGif.end)
    await send_end(message, state)


@router.callback_query(AddGif.description, F.data == "skip")
async def addgif_skip(call: CallbackQuery, state: FSMContext):
    await state.update_data({"description": ""})
    await state.set_state(AddGif.end)
    await call.answer()
    await send_end(call.message, state)

    
async def send_end(message: Message, state: FSMContext):
    if await state.get_state() != AddGif.end:
        return
    
    data = await state.get_data()
    text = (
        "🍌 <b>Ваша гиф:</b>\n\n"
        f"<i>Название: </i> {data['title']}\n"
        f"<i>Описание: </i> {data['description']}\n\n"
        "<b><i>Отправлять админам на проверку?</i></b>"
    )
    await message.answer_animation(
        data["gif"],
        caption=text,
        reply_markup=inline_builder(["Отправляем", "send_to_admins"])
    )
    

@router.callback_query(AddGif.end, F.data == "send_to_admins")
async def send_to_admins(call: CallbackQuery, user: User, state: FSMContext):
    data = await state.get_data()
    gif = Gif(
        user=user,
        gif_id=(await get_last_gif_id()) + 1,
        file_id=data["gif"],
        title=data["title"],
        description=data["description"]
    )
    await gif.insert()
    
    caption = (
        f"🍌 <b>Гиф от пользователя {user.user_id}:</b>\n\n"
        f"<i>Название: </i> {data['title']}\n"
        f"<i>Описание: </i> {data['description']}\n\n"
    )
    
    bot = call.bot
    await bot.send_animation(
        chat_id=admin,
        animation=gif.file_id,
        caption=caption,
        reply_markup=inline_builder(
            ["Принять", f"accept_gif:{gif.gif_id}:yes"],
            ["Отклонить", f"accept_gif:{gif.gif_id}:no"]
        )
    )
    
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("<b>Гиф успешно отправлена администрации!</b>")



@router.callback_query(F.data.startswith("accept_gif:"), F.from_user.id.in_([admin]))
async def accept_gif_call(call: CallbackQuery, state: FSMContext):
    gif = await Gif.find_one(Gif.gif_id == int(call.data.split(":")[1]), fetch_links=True)
    if not gif:
        print(gif)
        await call.answer()
        return
    
    action = call.data.split(":")[2]
    
    await call.answer()
    if action == "yes":
        gif.verified = True
        await gif.save()
        await call.bot.send_message(gif.user.user_id, f"<b>Вашу гиф с названием </b><code>{gif.title}</code><b> успешно приняли. Теперь она есть в /catalog</b>")
        await call.message.edit_reply_markup(reply_markup=None)
    elif action == "no":
        await call.message.answer("<i>Введите причину:</i>")
        await state.clear()
        await state.set_data({"gif_id": gif.gif_id})
        await state.set_state(Reason.reason)


@router.message(Reason.reason, F.text)
async def accept_gif_no(message: Message, state: FSMContext):
    data = await state.get_data()
    gif =  await Gif.find_one(Gif.gif_id == data["gif_id"], fetch_links=True)
    reason = message.text
    
    await gif.delete()
    await message.bot.send_message(
        gif.user.user_id, 
        f"<b>К сожалению, вашу гиф с названием {gif.title} не приняли :(</b>\n\nПричина: {reason}"
    )
    await message.reply("✅ <b>Успешно</b>")
    await state.clear()
