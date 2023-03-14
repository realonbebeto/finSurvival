import requests
import streamlit as st
import schemas
from core.config import settings
from email_validator import validate_email, EmailNotValidError

st.set_page_config(
    page_title="Finlytik: Credit Risk App",
    page_icon="./credit-cards.png",
    initial_sidebar_state="expanded"
)

headerSection = st.container()
mainSection = st.container()
reportsSection = st.container()
loginSection = st.container()
logOutSection = st.container()
registerSection = st.container()


def show_main_page():
    with st.form(key="profile_form"):
        age = st.number_input("What is your age?", format="%i", min_value=0)
        annual_income = st.number_input(
            "What is your annual income?", format="%f", min_value=0.0)
        num_bank_accounts = st.number_input(
            "What is the number of your bank accounts?", format="%i", min_value=0)
        num_credit_card = st.number_input(
            "What is the number of your credit cards?", format="%i", min_value=0)
        interest_rate = st.number_input(
            "What is the interest rate of your loan?", format="%f", min_value=0.0)
        num_of_loan = st.number_input(
            "What is the number of your active loans?", format="%i", min_value=0)
        num_of_delayed_payment = st.number_input(
            "What is the number of your past deliquencies?", format="%i", min_value=0)
        changed_credit_limit = st.number_input(
            "How many times has your credit limit changed?", format="%i", min_value=0)
        num_credit_inquiries = st.number_input(
            "How many times have you enquired for loans?", format="%i", min_value=0)
        credit_mix = st.selectbox(
            "What is the spread of your loans?", ('Bad', 'Good', 'Standard'))
        outstanding_debt = st.number_input(
            "What is your current outstanding amount?", format="%f", min_value=0.0)
        credit_utilization_ratio = st.number_input(
            "What is your credit utilization ratio?", format="%f", min_value=0.0)
        credit_history_age = st.number_input(
            "What is the number of years you have used credit", format="%i", min_value=0)
        payment_of_min_amount = st.selectbox(
            'Did you pay the minimum amount only?',
            ('Yes', 'No', 'Other'))
        total_emi_per_month = st.number_input(
            "What is your current monthly constant payment towards loan repayment?", format="%f", min_value=0.0)
        amount_invested_monthly = st.number_input(
            "What is the average amount you invest monthly?", format="%f", min_value=0.0)
        payment_behaviour = st.selectbox(
            'Whats your payment behaviour?',
            ('High_spent_Large_value_payments', 'High_spent_Medium_value_payments', 'High_spent_Small_value_payments', 'Low_spent_Large_value_payments', 'Low_spent_Medium_value_payments', 'Low_spent_Small_value_payments'))
        monthly_balance = st.number_input(
            "Insert the amount in your accounts", format="%i", min_value=0)
        analyseClicked = st.form_submit_button(label="Analyse")
    if analyseClicked:
        st.write("Analysis started... You will receive your report on mail")
        model_data = schemas.ProfileModel(age=age,
                                          annual_income=annual_income,
                                          monthly_inhand_salary=annual_income/12,
                                          num_bank_accounts=num_bank_accounts,
                                          num_credit_card=num_credit_card,
                                          interest_rate=interest_rate,
                                          num_of_loan=num_of_loan,
                                          num_of_delayed_payment=num_of_delayed_payment,
                                          changed_credit_limit=changed_credit_limit,
                                          num_credit_inquiries=num_credit_inquiries,
                                          credit_mix=credit_mix,
                                          outstanding_debt=outstanding_debt,
                                          credit_utilization_ratio=credit_utilization_ratio,
                                          credit_history_age=credit_history_age,
                                          payment_of_min_amount=payment_of_min_amount,
                                          total_emi_per_month=total_emi_per_month,
                                          amount_invested_monthly=amount_invested_monthly,
                                          payment_behaviour=payment_behaviour,
                                          monthly_balance=monthly_balance)
        response = requests.post(
            f"http://{settings.GATEWAY_SVC_ADDRESS}/infer", json=model_data.dict())

        if response.status_code == 200:
            st.success(
                'Successful: Your request is being processed and will be sent to your email')
        else:
            st.error('Error: Try again later')


def show_reports_page():
    with st.form(key="reports_form"):
        number = st.number_input(
            label="Number of Reports", format="%i", min_value=0)
        reports = st.form_submit_button(label="View Reports")

    if reports:
        r_body = {'limit': number}
        response = requests.post(
            f"http://{settings.GATEWAY_SVC_ADDRESS}/reports", json=r_body)
        if response.status_code == 200:
            # Collect the scores and plot and paginate the plots
            risk, survival, hazard = st.beta_columns((1, 3, 3, ))
            last_page = len(response.json()['profiles']) // 1

            pass
        else:
            st.warning("Send a Credit Profile with us to view reports")


def LoggedOut_Clicked():
    st.session_state['loggedIn'] = False


def show_logout_page():
    loginSection.empty()
    with st.form(key="logout_form"):
        st.form_submit_button(label="Log Out", on_click=LoggedOut_Clicked)


def LoggedIn_Clicked(username: str, password: str):
    basic_auth = {'username': username,
                  'password': password}
    response = requests.post(
        f"http://{settings.GATEWAY_SVC_ADDRESS}/login", data=basic_auth
    )

    if response.status_code == 200:
        st.session_state['loggedIn'] = True
    else:
        st.session_state['loggedIn'] = False
        st.error("Invalid user name or password")


def email_validate(email: str):
    try:
        emailObject = validate_email(email, check_deliverability=True)
        return emailObject.email
    except EmailNotValidError:
        return None


def SignUp_Clicked(full_name: str, email: str, password: str):
    email = email_validate(email)
    if email:
        try:
            basic_auth = {'full_name': full_name,
                          'email': email,
                          'password': password}
            response = requests.post(
                f"http://{settings.GATEWAY_SVC_ADDRESS}/register", json=basic_auth)
            if response.status_code == 200:
                st.success("Sign Up Successful")
            else:
                st.error("Sign Up Unsuccessful. Try again later.")
        except:
            st.error("Internal Server Error. Sign Up Failed. Try again later.")
    else:
        st.error("Enter a valid email address")


def show_login_page():
    if st.session_state['loggedIn'] == False:
        with st.form(key="login_form", clear_on_submit=True):
            username = st.text_input(
                label="Email or Username", value="", placeholder="Enter your email address", key="username")
            password = st.text_input(
                label="Password", value="", placeholder="Enter password", type="password", key="passwordl")
            login = st.form_submit_button(label="Login")
            if login:
                LoggedIn_Clicked(username, password)


def show_register_page():
    if st.session_state['loggedIn'] == False:
        with st.form(key='register_form', clear_on_submit=True):
            full_name = st.text_input(
                label="Full Name", value="", placeholder="Enter your full name", key="full_name")
            email = st.text_input(
                label="Email", value="", placeholder="Enter your email address", key="email")
            password = st.text_input(
                label="Password", value="", placeholder="Enter password", type="password", key="password")
            sign_up = st.form_submit_button(label='Sign Up')
            if sign_up:
                SignUp_Clicked(full_name, email, password)


def main():
    with headerSection:
        st.title("Finlytik: Credit Risk")

    if 'loggedIn' not in st.session_state:
        st.session_state['loggedIn'] = False
        login, register = st.tabs(["Login", "Register"])
        with login:
            show_login_page()
        with register:
            show_register_page()
    else:
        if st.session_state['loggedIn']:
            main, reports, logout = st.tabs(["Login", "Reports", "Logout"])
            with main:
                show_main_page()
            with reports:
                show_reports_page()
            with logout:
                show_logout_page()

        else:
            login, register = st.tabs(["Login", "Register"])
            with login:
                show_login_page()
            with register:
                show_register_page()


if __name__ == "__main__":
    try:
        main()
    except:
        st.error(
            'Oops! Something went wrong...Please check your input.\nIf you think there is a bug, please open up an [issue](https://github.com/realonbebeto/finSurvival/issues) and help us improve. ')
        raise
