# https://github.com/ggrammar/pizzapi
from pizzapi import *
from credentials import *


def decode_message(message):
    message = message.title().strip()
    common_phrases = ["Can I Have A", "Could I Have A", "Could I Get A", "And", "Some"]
    for phrase in common_phrases:
        message = message.replace(phrase, "")
    items = message.split(",")
    return items


def edit_distance_dp(str1, str2, m, n):
    # Create a table to store results of subproblems 
    dp = [[0 for x in range(n + 1)] for x in range(m + 1)]
    # Fill d[][] in bottom up manner 
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                dp[i][j] = j  # Min. operations = j
            elif j == 0:
                dp[i][j] = i  # Min. operations = i
            elif str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i][j - 1],  # Insert
                                   dp[i - 1][j],  # Remove
                                   dp[i - 1][j - 1])  # Replace
    return dp[m][n]


def get_names_preconfigured(user):
    names_to_ids = {}
    preconfigured = user.menu.__dict__["preconfigured"]
    for item in range(len(preconfigured)):
        try:
            current = preconfigured[item].__dict__
            names_to_ids[current["name"]] = current["code"]
        except:
            print("ERROR")
    products = user.menu.__dict__["products"]
    for item in range(len(products)):
        try:
            current = products[item].__dict__
            names_to_ids[current["name"]] = current["code"]
        except:
            print("ERROR1")
    return names_to_ids


def ids_to_variants(user):
    ids_to_variants = {}
    variants = user.menu.__dict__["variants"]
    for item in variants:
        if variants[item]["ProductCode"] in ids_to_variants:
            ids_to_variants[variants[item]["ProductCode"]].append(item)
        else:
            ids_to_variants[variants[item]["ProductCode"]] = [item]
    return ids_to_variants


def item_to_ids(items, user):
    """
    Small - 10" / 25 cm.
    Medium - 12" / 30 cm.
    Large - 14" / 35 cm.
    X-Large - 16" / 40 cm
    """
    sizes = ["10", "12", "14", "16", "25", "30", "35", "40"]
    if not items:
        return []
    ids = []
    names_to_id_product = get_names_preconfigured(user)
    for item in items:
        for name, product_id in names_to_id_product.items():
            # CLEAN TO REMOVE SMALL MEDIUM LARGE, AND STRIP
            item = item.strip()
            for size in sizes:
                if size in item:
                    if size == "10" or size == "25":
                        replace = "Small"
                    elif size == "12" or size == "30":
                        replace = "Medium"
                    elif size == "14" or size == "35":
                        replace = "Large"
                    elif size == "16" or size == "40":
                        replace = "X-Large"
                    item = item.replace(size + '"', replace).replace(size + "'", replace)
            # print(item, " | ", name, editDistanceDP(item, name, len(item), len(name)) / (len(name)))
            if edit_distance_dp(item, name, len(item), len(name)) / (len(name)) < .3 or edit_distance_dp(
                    item.replace("Pizza", ""), name.replace("Dipping ", ""), len(item.replace("Pizza", "")),
                    len(name.replace("Dipping ", ""))) / (len(name)) < .1:
                ids.append(product_id)
                break
    final_ids = []
    for id in ids:
        if "F_" in id:
            variants = ids_to_variants(user)
            replace = variants[id][0]
            if replace == "STJUDE":
                replace = "STJUDE10"
            final_ids.append(replace)
        else:
            final_ids.append(id)
    return final_ids
    # order.add_item('P12IPAZA') # add a 12-inch pan pizza
    # order.add_item('MARINARA') # with an extra marinara cup
    # order.add_item('20BCOKE')  # and a 20oz bottle of coke
    return ['P12IPAZA', 'MARINARA', '20BCOKE']


def intro():
    return "Hey! What would you like from Domino's?"


def format_text_back(result):
    name = result["Order"]["FirstName"]
    price = result["Order"]["AmountsBreakdown"]["Customer"]
    delivery_location = result["Order"]["Address"]["Street"] + " " \
                        + result["Order"]["Address"]["City"] + ", " \
                        + result["Order"]["Address"]["Region"]
    delivery_location = "your house"
    donation = None
    products = result["Order"]["Products"]
    products_list = []
    for product in products:
        if "Donation" not in product["Name"]:
            products_list.append(product["Name"])
        else:
            donation = product["Name"]
    products_clean = ", ".join(products_list)
    products_clean = ', and'.join(products_clean.rsplit(',', 1))
    message = f"Sup, {name}. You will receive {products_clean} in 30 minutes at {delivery_location}. " \
              "Make sure to tip the driver!"
    if donation:
        message += f" Thanks for the {donation}, you rock."
    print(price)
    return message


class Credentials:
    def __init__(self):
        self.FIRST_NAME = FIRST_NAME
        self.LAST_NAME = LAST_NAME
        self.EMAIL = EMAIL
        self.PHONE_NO = PHONE_NO
        self.STREET = STREET
        self.CITY = CITY
        self.STATE = STATE
        self.ZIP_CODE = ZIP_CODE

        self.CARD_NO = CARD_NO
        self.EXPIRATION = EXPIRATION
        self.CVC = CVC

        self.customer = Customer(self.FIRST_NAME, self.LAST_NAME, self.EMAIL, self.PHONE_NO)
        self.address = Address(self.STREET, self.CITY, self.STATE, self.ZIP_CODE)
        self.store = self.address.closest_store()
        self.card = PaymentObject(self.CARD_NO, self.EXPIRATION, self.CVC, self.ZIP_CODE)
        self.order = Order(self.store, self.customer, self.address)
        self.menu = self.store.get_menu()


def get_menu():
    user = Credentials()
    preconfigured = get_names_preconfigured(user)
    variants = ids_to_variants(user)
    for key, val in preconfigured.items():
        if "F_" in val:
            if len(variants[val]) > 1:
                preconfigured[key] = variants[val]
            else:
                preconfigured[key] = variants[val][0]
    menu_items = ["Here is the menu!\n" \
                  "To order with ProductCode write 'finalOrder:' followed by the codes on the left of the ':'\n"]
    for key, val in preconfigured.items():
        menu_items.append(key + " : " + str(val))
    return "\n".join(menu_items)


def app_options():
    help_menu_message = "THIS IS THE HELP MENU\nThese are your options"
    return help_menu_message


def order_pizza(textMessage):
    if not textMessage:
        return "NO MESSAGE"
    # STEP 1: Create User
    user = Credentials()
    # STEP 2: DECODE MESSSAGE TO GET ORDER ITEMS AND ADD TO ORDER
    items = decode_message(textMessage)  # pass back a list
    item_ids = item_to_ids(items, user)  # pass back a list
    if not item_ids and "finalOrder:" not in textMessage:
        return "Sorry we don't understand what you are asking for.\n" \
               "Try again and separate each item with a comma (,)."
    for item in item_ids:
        user.order.add_item(item)
    # user.order.add_item('STJUDE10')
    # STEP 3: ORDER THE PIZZA
    # REAL PAY 
    # order.place(card) #ONLY USE WHEN YOU WANT TO PAY 
    # TEST PAY 
    # result = user.order.place(user.card) #WHEN YOU WANT TO PAY 
    result = user.order.pay_with(user.card)  # USE FOR TEST
    # STEP 4: TEXT BACK CONFIRMATION TO THE USER 
    confirmation_text = format_text_back(result)
    return confirmation_text


if __name__ == "__main__":
    textMessage = "Could I get a 12' Cheese Pan Pizza, Marinara Sauce, Coke, and St. Jude Donation"
    print(order_pizza(textMessage))
    print()
