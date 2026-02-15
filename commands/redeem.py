from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatType
from db import get_user, update_coins, set_rank

# Hardcoded costs
RANK_COSTS = {
    "General": 5000,
    "Major": 10000,
    "Elite": 20000,
    "Mr. Money Man": 100000
}

TIME_COSTS = {
    "Daily": 1.0,
    "Weekly": 1.5,
    "Monthly": 2.5
}

# Temporary user redeem state
REDEEM_STATE = {}

# Step 1: /redeem command
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user:
        await update.message.reply_text("❌ You are not registered yet.")
        return

    # Inline buttons for main redeem menu
    keyboard = [
        [
            InlineKeyboardButton("Status Upgrade", callback_data="status_upgrade"),
            InlineKeyboardButton("GIFTCARD", callback_data="giftcard")
        ]
    ]
    REDEEM_STATE[user_id] = {"step": "main"}  # track flow
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select what you want to redeem:", reply_markup=reply_markup)


# Callback handler for inline buttons
async def redeem_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query.data.startswith("redeem_"):
        return
    await query.answer()  # acknowledge button press
    user_id = query.from_user.id
    data = query.data

    if user_id not in REDEEM_STATE:
        return  # user not in flow

    state = REDEEM_STATE[user_id]

    # Main menu selections
    if state["step"] == "main":
        if data == "status_upgrade":
            keyboard = [
                [
                    InlineKeyboardButton(f"General ({RANK_COSTS['General']} coins)", callback_data="rank_General"),
                    InlineKeyboardButton(f"Major ({RANK_COSTS['Major']} coins)", callback_data="rank_Major")
                ],
                [
                    InlineKeyboardButton(f"Elite ({RANK_COSTS['Elite']} coins)", callback_data="rank_Elite"),
                    InlineKeyboardButton(f"Mr. Money Man ({RANK_COSTS['Mr. Money Man']} coins)", callback_data="rank_MrMoneyMan")
                ]
            ]
            REDEEM_STATE[user_id]["step"] = "choose_rank"
            await query.edit_message_text("Choose the rank you want:", reply_markup=InlineKeyboardMarkup(keyboard))

        elif data == "giftcard":
            # Force private message
            if query.message.chat.type != ChatType.PRIVATE:
                keyboard = [[InlineKeyboardButton("📩 Message Bot", url="https://t.me/NORMAN_SBOT")]]
                await query.edit_message_text(
                    "🎁 Gift cards must be redeemed in private.",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                del REDEEM_STATE[user_id]
                return

            # If private, proceed
            REDEEM_STATE[user_id]["step"] = "giftcard_code"
            await query.edit_message_text("🎁 Send your gift card code now:")

    # Step 2: Choose rank
    elif state["step"] == "choose_rank" and data.startswith("rank_"):
        selected_rank = data.split("_")[1].replace("MrMoneyMan", "Mr. Money Man")
        cost = RANK_COSTS.get(selected_rank)
        user = get_user(user_id)

        if user["coins"] < cost:
            await query.edit_message_text(f"❌ Not enough coins. Required: {cost}, You have: {user['coins']}")
            del REDEEM_STATE[user_id]
            return

        REDEEM_STATE[user_id]["selected_rank"] = selected_rank
        REDEEM_STATE[user_id]["step"] = "choose_time"

        # Time options
        keyboard = [
            [
                InlineKeyboardButton(f"Daily ({int(cost*TIME_COSTS['Daily'])} coins)", callback_data="time_Daily"),
                InlineKeyboardButton(f"Weekly ({int(cost*TIME_COSTS['Weekly'])} coins)", callback_data="time_Weekly")
            ],
            [
                InlineKeyboardButton(f"Monthly ({int(cost*TIME_COSTS['Monthly'])} coins)", callback_data="time_Monthly"),
                InlineKeyboardButton("Cancel", callback_data="cancel")
            ]
        ]
        await query.edit_message_text(f"Choose duration for {selected_rank}:", reply_markup=InlineKeyboardMarkup(keyboard))

    # Step 3: Choose time
    elif state["step"] == "choose_time" and data.startswith("time_"):
        selected_rank = REDEEM_STATE[user_id]["selected_rank"]
        base_cost = RANK_COSTS[selected_rank]
        time_choice = data.split("_")[1]
        multiplier = TIME_COSTS.get(time_choice)
        total_cost = int(base_cost * multiplier)
        user = get_user(user_id)

        if user["coins"] < total_cost:
            await query.edit_message_text(f"❌ Not enough coins. Required: {total_cost}, You have: {user['coins']}")
            del REDEEM_STATE[user_id]
            return

        REDEEM_STATE[user_id]["total_cost"] = total_cost
        REDEEM_STATE[user_id]["time_choice"] = time_choice
        REDEEM_STATE[user_id]["step"] = "confirm"

        # Confirm buttons
        keyboard = [
            [
                InlineKeyboardButton("Confirm", callback_data="confirm"),
                InlineKeyboardButton("Cancel", callback_data="cancel")
            ]
        ]
        await query.edit_message_text(
            f"⚠️ You are about to spend {total_cost} coins to upgrade to {selected_rank} for {time_choice}.\nConfirm?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # Step 4: Confirm / Cancel
    elif state["step"] == "confirm":
        if data == "confirm":
            selected_rank = REDEEM_STATE[user_id]["selected_rank"]
            total_cost = REDEEM_STATE[user_id]["total_cost"]
            update_coins(user_id, get_user(user_id)["coins"] - total_cost)
            set_rank(user_id, selected_rank)
            await query.edit_message_text(
                f"✅ Success! Your rank is now {selected_rank}.\nCoins spent: {total_cost}"
            )
        else:
            await query.edit_message_text("❌ Redeem cancelled.")

        del REDEEM_STATE[user_id]

    # Cancel button
    elif data == "cancel":
        await query.edit_message_text("❌ Redeem cancelled.")
        del REDEEM_STATE[user_id]
