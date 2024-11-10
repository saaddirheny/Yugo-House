from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem, OneLineAvatarIconListItem, IRightBodyTouch
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.button import MDFlatButton
from kivymd.uix.datatables import MDDataTable
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivymd.uix.toolbar import MDTopAppBar
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.modalview import ModalView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDCheckbox

from datetime import datetime

from kivymd.uix.pickers import MDDatePicker

import requests
import json

import firebase_admin
from firebase_admin import credentials, db

from kivy.properties import StringProperty

# Path to your Firebase Admin SDK key
cred = credentials.Certificate("Firebase/yugohousefirebase.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://yugo-house-default-rtdb.firebaseio.com'
})


#Fees List With ON/OFF Switch 
class SwitchItem(OneLineListItem):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initializing_switch = True

    def show_the_popup(self, message,topic):
        self.dialog = MDDialog(
            title = topic,
            radius=[20,20,20,20],
            text=message,
            size_hint=(0.8, None),
            height=dp(50),
            auto_dismiss=True,
            buttons=[
                MDFlatButton(
                    text="Close", on_release=lambda *args: self.dialog.dismiss()
                )
            ],
        )
        self.dialog.open()



    def on_switch_active(self, active):
        if self.initializing_switch:
            return
        
        print(f"Switch {self.text} is {'on' if active else 'off'}")
        session = datetime.now().strftime('%m-%Y')
        nameid = self.text
        payment_url = f"https://yugo-house-default-rtdb.firebaseio.com/Payments/{session}/{nameid}.json"
        
        payornot= {
            "Payment" : f"{'Paid' if active else 'Unpaid'}"
        }

        response = requests.put(url=payment_url, json=payornot)
        
        if response.status_code == 200:
            print(f"{nameid} paid successfully.")
        else:
            print(f"Failed to pay: {response.text}")



        total_amount_url = "https://yugo-house-default-rtdb.firebaseio.com/Details/TotalAmount.json"
        
        # Fetch the current amount from Firebase
        response = requests.get(total_amount_url)
        if response.status_code == 200:
            current_data = response.json()
            current_amount = current_data.get("Amount", 0)

        else:
            current_amount = 0

        fee_amount_url = "https://yugo-house-default-rtdb.firebaseio.com/FeesAmount.json"
        fixedfee = requests.get(fee_amount_url)
        if fixedfee.status_code == 200:
            current_fee = fixedfee.json()
            fixedfeess = current_fee.get("FeeAmount", 0)
            fixedfees = int(fixedfeess)
        else:
            print(f"Failed to fetch current data: {response.text}")
            fixedfees = 0


        # Calculate the new amount
        amount_change = fixedfees if active else -(fixedfees)
        new_amount = current_amount + amount_change

        detailsinput = {
            "Amount": new_amount
        }

        requests.put(url=total_amount_url, json=detailsinput)

        if response.status_code == 200:
            if amount_change > 0 :
                self.show_the_popup(f"{nameid} Paid Rs.{amount_change} successfully.","Payment Received" )
            else:
                self.show_the_popup(f"{nameid} Retrieved Rs.{-(amount_change)}", "Warning")
        else:
            self.show_the_popup("Something Wrong", "Error")


#Spend_Amounts............................................

class Login_Screen(Screen):
    pass

class Main_Screen(Screen):
    pass

class Detail_Screen(Screen):
    pass

class Spend_Amounts(Screen):
    pass

class Add_New_Member(Screen):
    pass

class EditOptions(Screen):
    pass

class FeeFine(Screen):
    pass

class Fees(Screen):
    pass

class Fee_Editing(Screen):
    pass

class Fine_Editing(Screen):
    pass

class ErrorPopup(ModalView):
    pass

class DeleteMember(Screen):
    pass


class DeleteMembersItem(OneLineAvatarIconListItem):
    def __init__(self, text, **kwargs):
        super().__init__(text=text, **kwargs)
        self.checkbox = MDCheckbox(size_hint=(None, None), size=("48dp", "48dp"))
        self.add_widget(self.checkbox)
        self.checkbox.pos_hint = {"center_y": 0.5}
        self.checkbox.disabled = True

#Main App .........................................................

class MainApp(MDApp):
    apsy_url = "https://yugo-house-default-rtdb.firebaseio.com/.json"

    current_date = datetime.now().strftime('%m-%Y')
    current_amount = StringProperty()
    expanse_amount = StringProperty()
    remain_amount = StringProperty()
    totalmembers = StringProperty()

    
    def on_start(self):
        self.refresh_data()
        self.update_member_names()
        self.update_deletion_member_names()
        self.totalstudents()

    def show_the_popup(self, message,topic):
        self.dialog = MDDialog(
            title = topic,
            radius=[20,20,20,20],
            text=message,
            size_hint=(0.8, None),
            height=dp(50),
            auto_dismiss=True,
            buttons=[
                MDFlatButton(
                    text="Close", on_release=lambda *args: self.dialog.dismiss()
                )
            ],
        )
        self.dialog.open()

    def totalstudents(self):
        members_names = "https://yugo-house-default-rtdb.firebaseio.com/MembersInformations.json"
        items_data = requests.get(members_names).json()
        items = list(items_data.keys())
        total_member = len(items)
        self.totalmembers = str(total_member)


    def update_member_names(self):
        members_names = "https://yugo-house-default-rtdb.firebaseio.com/MembersInformations.json"
        
        try:
            items_data = requests.get(members_names).json()
            items = list(items_data.keys())

#        item = ['Saad Ibrahim', 'Qasim Ali', 'Asfan Rahi', 'Balti Boy','Saad Ibrahim', 'Qasim Ali', 'Asfan Rahi', 'Balti Boy']
            screen = self.root.get_screen("add_fee")
            screen.ids.add_fee_list.clear_widgets()
            for item in items:
                switch_item = SwitchItem(text=item) 
                screen.ids.add_fee_list.add_widget(switch_item)

                session = datetime.now().strftime('%m-%Y')
                payment_url = f"https://yugo-house-default-rtdb.firebaseio.com/Payments/{session}.json"


                switch_item.initializing_switch = True
                response = requests.get(url=payment_url)
                if response.status_code == 200:
                    data = response.json()
                    for name, info in data.items():
                        if name == item:
                            if info['Payment'] == "Paid":
                                switch_item.ids.switch.active = True

                            elif info['Payment'] == "Unpaid":
                                switch_item.ids.switch.active = False
                else:
                    print(f"Failed to fetch state: {response.text}")

                switch_item.initializing_switch = False
        except:
            pass


#Total Remain Amount to Display in Detail Section
    def update_total_amount(self):
        details_url = "https://yugo-house-default-rtdb.firebaseio.com//Details/TotalAmount.json"
        # Fetch the current amount from Firebase
        response_total = requests.get(details_url)
        if response_total.status_code == 200:
            current_data = response_total.json()
            current_data_str = current_data.get("Amount", 0)
            self.current_amount = str(current_data_str)


#Total Expanses Amount to Display in Detail Section
    def update_expanse_amount(self):
        details_url = "https://yugo-house-default-rtdb.firebaseio.com//Details/Expanses.json"
        # Fetch the current amount from Firebase
        response_expanse = requests.get(details_url)
        if response_expanse.status_code == 200:
            expanses_data = response_expanse.json()
            expanses_data_str = expanses_data.get("Expanses", 0)
            self.expanse_amount = str(expanses_data_str)

#Total Remaining Amount to Display in Detail Section
    def update_remaining_amount(self):
        remains_url = "https://yugo-house-default-rtdb.firebaseio.com//Details/Remaining.json"
        # Fetch the current amount from Firebase
        response_remaining = requests.get(remains_url)
        if response_remaining.status_code == 200:
            remain_data = response_remaining.json()
            remain_data_str = remain_data.get("Remain", 0)
            self.remain_amount = str(remain_data_str)

    def refresh_data(self):
        self.update_total_amount()
        self.update_expanse_amount()
        self.remainingsupdate()
        self.update_remaining_amount()


#Member Deletion////////////////////////////////////////////






    def update_deletion_member_names(self):
        members_names = "https://yugo-house-default-rtdb.firebaseio.com/MembersInformations.json"
        
        # Fetch the data from Firebase
        try:
            items_data = requests.get(members_names).json()
            items = list(items_data.keys())

            # Get the screen and the list widget
            screen = self.root.get_screen("delete_member")
            
            # Clear the existing items
            screen.ids.add_fee_list.clear_widgets()

            # Add the new items
            for item in items:
                switch_item = DeleteMembersItem(text=item) 
                screen.ids.add_fee_list.add_widget(switch_item)
        except:
            pass
    
    def enable_delete_mode(self):
        screen = self.root.get_screen("delete_member")
        for child in screen.ids.add_fee_list.children:
            if isinstance(child, DeleteMembersItem):
                child.checkbox.disabled = False
        screen.ids.confirm_delete_button.disabled = False
    
    def confirm_deletion(self):
        screen = self.root.get_screen("delete_member")
        items_to_delete = []
        for child in screen.ids.add_fee_list.children:
            if isinstance(child, DeleteMembersItem) and child.checkbox.active:
                items_to_delete.append(child.text)
        
        # Now you have the items to delete in items_to_delete list
        # Perform deletion from Firebase or any other necessary action
        
        for item in items_to_delete:
            self.delete_item_from_firebase(item)

        # Update the member names after deletion
        self.update_member_names()
        self.update_deletion_member_names()

    def delete_item_from_firebase(self, item):
        # Add logic to delete item from Firebase
        # For example, if your data structure allows:
        requests.delete(f"https://yugo-house-default-rtdb.firebaseio.com/MembersInformations/{item}.json")
        




    def build(self):
        self.theme_cls.primary_palette = "Blue"
        screens = ScreenManager()
        
        Builder.load_file('Screens/loginscreen.kv')
        Builder.load_file('Screens/mainscreen.kv')
        Builder.load_file('Screens/spend.kv')
        Builder.load_file('Screens/addnewmember.kv')
        Builder.load_file('Screens/editoptions.kv')
        Builder.load_file('Screens/feesandfine.kv')
        Builder.load_file('Screens/fineediting.kv')
        Builder.load_file('Screens/feefine.kv')
        Builder.load_file('Screens/fees.kv')
        Builder.load_file('Screens/detail_screen.kv')
        Builder.load_file('Screens/deletemembers.kv')

        screens.add_widget(Login_Screen(name='login_screen'))
        screens.add_widget(Main_Screen(name='main_screen'))
        screens.add_widget(Detail_Screen(name='detail_screen'))
        screens.add_widget(Spend_Amounts(name='spend_amount'))
        screens.add_widget(Add_New_Member(name='add_new_member'))
        screens.add_widget(EditOptions(name='edit_options'))
        screens.add_widget(FeeFine(name='fee_fine'))
        screens.add_widget(Fee_Editing(name='feeediting'))
        screens.add_widget(Fine_Editing(name='fineediting'))
        screens.add_widget(Fees(name='add_fee'))
        screens.add_widget(DeleteMember(name='delete_member'))

        return screens
    
    def change_screen(self):
        self.root.current = 'main_screen'
        self.root.transition.direction = 'left'

    def delete_the_member(self):
        self.root.current = 'delete_member'
        self.root.transition.direction = 'left'

    def on_save(self, instance, value, date_range):
        date_str = value.strftime('%Y-%m-%d')
        self.save_date_to_firebase(date_str)
        print(f'Date {date_str} saved to Firebase.')

    def on_cancel(self, instance, value):
        print("Date picker was cancelled")

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        size_hint = 0.5, 0.5
        date_dialog.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

    #Gapppppppppppppppppppppppppppppppppppppp
    #Gapppppppppppppppppppppppppppppppppppppp
    #Gapppppppppppppppppppppppppppppppppppppp
    #Gapppppppppppppppppppppppppppppppppppppp
    #Gapppppppppppppppppppppppppppppppppppppp
    #Gapppppppppppppppppppppppppppppppppppppp
    #Gapppppppppppppppppppppppppppppppppppppp
    #Gapppppppppppppppppppppppppppppppppppppp
    #Gapppppppppppppppppppppppppppppppppppppp
    #Gapppppppppppppppppppppppppppppppppppppp
    #Gapppppppppppppppppppppppppppppppppppppp
    #Gapppppppppppppppppppppppppppppppppppppp
    #Gapppppppppppppppppppppppppppppppppppppp
    #Gapppppppppppppppppppppppppppppppppppppp
    #Gapppppppppppppppppppppppppppppppppppppp
    #Gapppppppppppppppppppppppppppppppppppppp

#Login Attempt
    def change_screen(self):
        # Access login_screen using its name
        try:
            login_screen = self.root.get_screen('login_screen')
            username = login_screen.ids.username.text.upper()
            mypassword = login_screen.ids.password.text
            admininfo = "AdminInfo"
            adminurl = f"https://yugo-house-default-rtdb.firebaseio.com/{admininfo}.json"
            admindata = requests.get(url=adminurl)
            admindatajson =admindata.json()

            usernamedata = admindatajson.get('username',None)
            passworddata = admindatajson.get('adminpassword',None)

            if username == usernamedata and passworddata == mypassword:
                self.root.current = 'main_screen'
                self.root.transition.direction = 'left'
            else:
                self.show_the_popup("Incorrect Username or Password", "Wrong!")
        except:
            self.show_the_popup("Something went Wrong!", "Invalid Attempt")


#Main Menu
    def main_menu(self):
        self.root.current = 'main_screen'
        self.root.transition.direction = 'right'

    def edit_options(self):
        self.root.current = 'edit_options'
        self.root.transition.direction = 'right'

    def add_new_student(self):
        self.root.current = 'add_new_member'
        self.root.transition.direction = 'left'

    def feeandfine(self):
        self.root.current = 'feeediting'
        self.root.transition.direction = 'left'

    def fineediting(self):
        self.root.current = 'fineediting'
        self.root.transition.direction = 'left'

    def feeandfineinfo(self):
        self.root.current = 'feeinfotable'
        self.root.transition.direction = 'left'

    def addfees(self):
        self.root.current = 'add_fee'
        self.root.transition.direction = 'left'

    def funds(self):
        self.root.current = 'fee_fine'
        self.root.transition.direction = 'right'

#////////////////////////////////////////////////

#Spend Amount ..............................................

    def expendituress(self):
        screen = self.root.get_screen('spend_amount')
        expends = "Expenditures"
        Spend_Year = datetime.now().strftime('%Y')
        Spend_Month = datetime.now().strftime('%m-%Y')
        Rupees = screen.ids.spend_rupees.text
        Goods = screen.ids.buy_what.text

        current_datetime = datetime.now().strftime('%d-%m-%Y (%H:%M:%S)')
        expenditures= {
            "Rs" : screen.ids.spend_rupees.text,
            "Bought" : screen.ids.buy_what.text,
            "Updated On" : current_datetime
        }

        if not Rupees:
            self.show_the_popup("Please Fill Properly","Invalid")
            return
        expenditure_url = f"https://yugo-house-default-rtdb.firebaseio.com/{expends}/{Spend_Year}/{Spend_Month}/{current_datetime}.json"
        
        response = requests.put(url=expenditure_url, json=expenditures)
        
        if response.status_code == 200:
            self.show_the_popup(f"Rs.{Rupees} Spend for {Goods}","Amount Deducted")
        else:
            self.show_the_popup("Something Wrong!","Error")


        expanses_url = "https://yugo-house-default-rtdb.firebaseio.com/Details/Expanses.json"
        response = requests.get(expanses_url)
        if response.status_code == 200:
            expanses_data = response.json()
            expanses_amount = expanses_data.get("Expanses", 0)
            update_expanses_amount = expanses_amount 

            overall_expanses = int(update_expanses_amount) + int(screen.ids.spend_rupees.text)
            
        detailsinput = {
            "Expanses": int(update_expanses_amount) + int(screen.ids.spend_rupees.text)
        }
        requests.put(url=expanses_url, json=detailsinput)

        remaining_url = "https://yugo-house-default-rtdb.firebaseio.com/Details/Remaining.json"
        total_amount_url = "https://yugo-house-default-rtdb.firebaseio.com/Details/TotalAmount.json"
        total_amount = requests.get(total_amount_url)
        if total_amount.status_code == 200:
            total_amount_data = total_amount.json()
            total_amounts = total_amount_data.get("Amount", 0)
            update_total_amount = total_amounts  
            
        remain_data_input = {
            "Remain": int(update_total_amount) - int(overall_expanses)
        }
        requests.put(url=remaining_url, json=remain_data_input)


#Remaining Update ////////////////////////////////

    def remainingsupdate(self):
        expanses_url = "https://yugo-house-default-rtdb.firebaseio.com/Details/Expanses.json"
        response = requests.get(expanses_url)
        if response.status_code == 200:
            expanses_data = response.json()
            expanses_amount = expanses_data.get("Expanses", 0)

        remaining_url = "https://yugo-house-default-rtdb.firebaseio.com/Details/Remaining.json"
        total_amount_url = "https://yugo-house-default-rtdb.firebaseio.com/Details/TotalAmount.json"
        total_amount = requests.get(total_amount_url)
        if total_amount.status_code == 200:
            total_amount_data = total_amount.json()
            total_amounts = total_amount_data.get("Amount", 0)
            update_total_amount = total_amounts  
            
        remain_data_input = {
            "Remain": int(update_total_amount) - int(expanses_amount)
        }
        requests.put(url=remaining_url, json=remain_data_input)




#Add New Member ..............................................

    def addnewmembers(self):
        screen = self.root.get_screen('add_new_member')
        memberinfo = "MembersInformations"
        Info = screen.ids.name.text +" "+screen.ids.father_name.text
        member_data= {
            "Name" : screen.ids.name.text,
            "Father Name" : screen.ids.father_name.text,
            "Work Place" : screen.ids.work_place.text,
            "Contact No" : screen.ids.contact_no.text,
        }

        add_member_url = f"https://yugo-house-default-rtdb.firebaseio.com/{memberinfo}/{Info}.json"
        
        response = requests.put(url=add_member_url, json=member_data)
        
        if response.status_code == 200:
            self.update_deletion_member_names()
            self.show_the_popup(f"{Info} added Sucessfully!","Done")
        else:
            self.show_the_popup("Something Wrong!","Error")

#Spend Amount ........................................................

    def addfunds(self):
        screen = self.root.get_screen('spend_amount')
        amounts = screen.ids.fee_amount.text
        amounts_data= {
            "Amount" : screen.ids.spend_rupees.text,
        }
        details = "Details"
        add_funds_url = f"https://yugo-house-default-rtdb.firebaseio.com/{details}.json"
        
        response = requests.put(url=add_funds_url, json=amounts_data)

        if response.status_code == 200:
            self.show_the_popup(f"Fund of {amounts} added successfully.", "Fund Added")
        else:
            self.show_the_popup("Something Wrong!","Error")

#Fee Amount ........................................................

    def addedfees(self):
        screen = self.root.get_screen('feeediting')
        amounts = screen.ids.fee_amount.text
        amounts_data= {
            "FeeAmount" : screen.ids.fee_amount.text,
        }
        details = "FeesAmount"
        add_fees_url = f"https://yugo-house-default-rtdb.firebaseio.com/{details}.json"
        
        response = requests.put(url=add_fees_url, json=amounts_data)

        if response.status_code == 200:
            self.show_the_popup(f"Fees Rs.{amounts} Fixed!","Done")
        else:
            self.show_the_popup("Something Wrong!","Error")

MainApp().run()