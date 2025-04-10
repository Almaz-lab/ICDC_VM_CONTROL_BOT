import telebot
from telebot import types
import os
from dotenv import load_dotenv
from get_vms import get_vms
from get_tech_support_vms import get_tech_support_vms
from get_presale_vms import get_presale_vms
import start_vm 
import stop_vm
import logging
import get_token
import threading


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USERS = [int(x) for x in os.getenv("ADMIN_USERS", "").split(",") if x.strip()]
TECH_SUPPORT_USERS = [int(x) for x in os.getenv("TECH_SUPPORT_USERS", "").split(",") if x.strip()]
PRESALES_USERS = [int(x) for x in os.getenv("PRESALES_USERS", "").split(",") if x.strip()]

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable must be set")


bot = telebot.TeleBot(BOT_TOKEN)

def check_user_access(user_id):
    return user_id in ADMIN_USERS or user_id in TECH_SUPPORT_USERS or user_id in PRESALES_USERS

@bot.message_handler(commands=['start'])
def start_command(message):
    if not check_user_access(message.from_user.id):
        bot.reply_to(message, "You are not authorized to use this bot.")
        return
    
    logger.info(f"User {message.from_user.id} started the bot")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    vm_button = types.KeyboardButton("VM's")
    markup.add(vm_button)
    bot.send_message(message.chat.id, "Welcome to PrimeBot! Click the VM's button to see the list of VMs.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "VM's")
def list_vms(message):
    if not check_user_access(message.from_user.id):
        bot.reply_to(message, "You are not authorized to use this function.")
        return
        
    try:
        logger.info(f"User {message.from_user.id} requested VM list")
       
        loading_msg = bot.send_message(message.chat.id, "Loading VMs, please wait...")
        
        
        if message.from_user.id in TECH_SUPPORT_USERS:
            vms = get_tech_support_vms()
        elif message.from_user.id in PRESALES_USERS:
            vms = get_presale_vms()
        else:
            vms = get_vms()
        
        if not vms:
            logger.warning("No VMs found")
            bot.edit_message_text("No VMs found.", message.chat.id, loading_msg.message_id)
            return
        
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        for vm in vms:
            
            vm_name = vm.get('name', 'Unknown VM')
            vm_id = vm.get('id', '')
            power_status = vm.get('power_status', '')
            
            if power_status in ['starting', 'start_complete']:
                vm_name = '🟢 ' + vm_name
            elif power_status in ['stopping', 'stop_complete']:
                vm_name = '🔴 ' + vm_name
            button = types.InlineKeyboardButton(text=vm_name, callback_data=f"vm_{vm_id}")
            markup.add(button)
        
        logger.info(f"Found {len(vms)} VMs")
        
        bot.edit_message_text(
            "Select a VM to view details:",
            message.chat.id,
            loading_msg.message_id,
            reply_markup=markup
        )
    except Exception as e:
        logger.error(f"Error fetching VMs: {str(e)}")
        bot.send_message(message.chat.id, f"Error fetching VMs: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('vm_'))
def vm_callback(call):
    if not check_user_access(call.from_user.id):
        bot.answer_callback_query(call.id, "You are not authorized to use this function.")
        return
        
    vm_id = call.data.split('_')[1]
    try:
        logger.info(f"User {call.from_user.id} requested details for VM {vm_id}")
        
        if call.from_user.id in TECH_SUPPORT_USERS:
            vms = get_tech_support_vms()
        elif call.from_user.id in PRESALES_USERS:
            vms = get_presale_vms()
        else:
            vms = get_vms()
        selected_vm = next((vm for vm in vms if str(vm.get('id', '')) == vm_id), None)
        
        if selected_vm:
            
            details = "VM Details:\n\n"
            for key, value in selected_vm.items():
                if key != 'id':  
                    details += f"{key}: {value}\n"
            
            # Create power control buttons
            markup = types.InlineKeyboardMarkup(row_width=2)
            power_on = types.InlineKeyboardButton(text="🟢 Power On", callback_data=f"power_on_{vm_id}")
            power_off = types.InlineKeyboardButton(text="🔴 Power Off", callback_data=f"power_off_{vm_id}")
            markup.add(power_on, power_off)
            
            logger.info(f"Successfully retrieved details for VM {vm_id}")
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, details, reply_markup=markup)
        else:
            logger.warning(f"VM {vm_id} not found")
            bot.answer_callback_query(call.id, "VM not found")
    except Exception as e:
        logger.error(f"Error fetching VM details: {str(e)}")
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"Error fetching VM details: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith(('power_on_', 'power_off_')))
def power_callback(call):
    if not check_user_access(call.from_user.id):
        bot.answer_callback_query(call.id, "You are not authorized to use this function.")
        return
        
    try:
        action, vm_id = call.data.split('_')[1:3]  
        logger.info(f"Power action requested: {action} for VM {vm_id}")
        
        if call.from_user.id in TECH_SUPPORT_USERS:
            vms = get_tech_support_vms()
        elif call.from_user.id in PRESALES_USERS:
            vms = get_presale_vms()
        else:
            vms = get_vms()
        selected_vm = next((vm for vm in vms if str(vm.get('id', '')) == vm_id), None)
        
        if selected_vm:
            power_status = selected_vm.get('power_status', '')
            
            if action == 'on' and power_status in ['start_complete', 'starting']:
                bot.answer_callback_query(call.id, "VM is already powered on")
            elif action == 'off' and power_status in ['stop_complete', 'stopping']:
                bot.answer_callback_query(call.id, "VM is already powered off")
            else:
                status_message = f"Attempting to power {action} VM {selected_vm.get('name', 'Unknown')}"
                bot.answer_callback_query(call.id, status_message)
                bot.send_message(call.message.chat.id, status_message)

                if action == 'on':
                    start_vm.start_vm(vm_id)
                    
                    bot.send_message(call.message.chat.id, f"Power on command was sent to virtual machine {selected_vm.get('name', 'Unknown')}")
                    
                else:
                    stop_vm.stop_vm(vm_id)
                    
                    bot.send_message(call.message.chat.id, f"Power off command was sent to virtual machine {selected_vm.get('name', 'Unknown')}")
                

        else:
            bot.answer_callback_query(call.id, "VM not found")
            
    except Exception as e:
        logger.error(f"Error handling power action: {str(e)}")
        bot.answer_callback_query(call.id, "Error processing power action")
        bot.send_message(call.message.chat.id, f"Error processing power action: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == "return_to_vms")
def return_to_vms_callback(call):
    if not check_user_access(call.from_user.id):
        bot.answer_callback_query(call.id, "You are not authorized to use this function.")
        return
    list_vms(call.message)
    bot.answer_callback_query(call.id)


if __name__ == "__main__":
    logger.info("Bot started")
    token_thread = threading.Thread(target=get_token.main)
    token_thread.daemon = True
    token_thread.start()
    bot.polling(none_stop=True)