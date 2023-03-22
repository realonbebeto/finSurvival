import requests
import streamlit as st
import schemas
from core.config import settings
from user import login
from email_validator import validate_email, EmailNotValidError
from streamlit_pagination import pagination_component
import pandas as pd

st.set_page_config(
    page_title="Finlytik: Credit Risk App",
    page_icon=":bar_chart:",
    initial_sidebar_state="expanded"
)
st.markdown('<style>' + open('/home/frontend/frontend/style.css').read() +
            '</style>', unsafe_allow_html=True)

headerSection = st.container()
mainSection = st.container()
reportsSection = st.container()
loginSection = st.container()
logOutSection = st.container()
registerSection = st.container()


def autHeader(token):
    return {'Authorization': f"Bearer {token}"}


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
        headers = autHeader(st.session_state["token"])
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
            f"http://{settings.GATEWAY_SVC_ADDRESS}/reports/infer", json=model_data.dict(), headers=headers)

        if response.status_code == 200:
            st.success(
                'Successful: Your request is being processed and will be sent to your email')
        else:
            st.error('Error: Try again later')


def show_reports_page():
    st.empty()
    number = st.number_input(label="Number of Reports",
                             format="%i", min_value=0)
    reports = st.button(label="View Reports")

    if reports:
        if number > 0:
            request_body = {'skip': 0, 'limit': int(number)}
            headers = autHeader(st.session_state["token"])
            response = requests.get(
                f"http://{settings.GATEWAY_SVC_ADDRESS}/reports/reports", params=request_body, headers=headers)
            if response.status_code == 200:
                if len(response.json()) > 0:
                    st.session_state["reports"] = response.json()
                else:
                    st.warning(
                        "No reports found. Send a Credit Profile with us to view reports")
            else:
                st.error("Try Again Later")
        else:
            st.warning('Cant fetch a 0 report')

    container = st.container()
    with container:
        if 'reports' not in st.session_state:
            st.empty()
            st.warning("No reports available")
        else:
            n = 1

            def data_chunk_choice():
                if 'pag' not in st.session_state:
                    return 0
                return st.session_state['pag']

            list_df = [st.session_state['reports'][i]
                       for i in range(0, len(st.session_state['reports']))]
            page = data_chunk_choice()
            max_page = len(list_df)

            if page > max_page:
                sub_data = list_df[max_page-1]
            else:
                sub_data = list_df[page]

            col1, col2, col3 = st.columns([1, 3, 3])
            with col1:
                if sub_data['risk_score']:
                    st.metric(label="Risk Score",
                              value=f"{sub_data['risk_score'][0]:.2f}")
                else:
                    st.write(None)
            with col2:
                if sub_data['times']:
                    st.subheader("Hazard Function")
                    st.write()
                    h_data = pd.DataFrame(
                        {'times': sub_data['times'], 'probability': sub_data['hazard_score']})
                    st.line_chart(h_data, x="times", y="probability")
                else:
                    st.write(None)
            with col3:
                if sub_data['times']:
                    st.subheader("Survival Function")
                    s_data = pd.DataFrame(
                        {'times': sub_data['times'], 'probability': sub_data['survival_score']})
                    st.line_chart(s_data, x="times", y="probability")
                else:
                    st.write(None)
            # st.write(sub_data)
            layout = {'color': "red",
                      'style': {'margin-top': '50px'}}
            test = pagination_component(
                len(list_df)+1, layout=layout, key="pag")


def LoggedOut_Clicked():
    st.session_state['loggedIn'] = False


def show_logout_page():
    loginSection.empty()
    with st.form(key="logout_form"):
        st.form_submit_button(label="Log Out", on_click=LoggedOut_Clicked)


def LoggedIn_Clicked(username: str, password: str):
    code, msg = login(username, password)
    if code == 200:
        st.session_state['token'] = msg
        st.session_state['loggedIn'] = True
    elif code == 401:
        st.session_state['loggedIn'] = False
        st.error("Invalid user name or password")
    else:
        st.error("Internal Server Error. Sign Up Failed. Try again later.")


def show_login_page():
    if st.session_state['loggedIn'] == False:
        username = st.text_input(
            label="Email or Username", value="", placeholder="Enter your email address", key="username")
        password = st.text_input(
            label="Password", value="", placeholder="Enter password", type="password", key="passwordl")
        st.button(
            label="Login", on_click=LoggedIn_Clicked, args=(username, password))


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
            elif response.status_code == 400:
                st.error("Email is not available. Please use another email")
            else:
                st.error("Sign Up Unsuccessful. Try again later.")
        except:
            st.error("Internal Server Error. Sign Up Failed. Try again later.")
    else:
        st.error("Enter a valid email address")


def show_register_page():
    if st.session_state['loggedIn'] == False:
        full_name = st.text_input(
            label="Full Name", value="", placeholder="Enter your full name", key="full_name")
        email = st.text_input(
            label="Email", value="", placeholder="Enter your email address", key="email")
        password = st.text_input(
            label="Password", value="", placeholder="Enter password", type="password", key="password")
        st.button(label='Sign Up', on_click=SignUp_Clicked,
                  args=(full_name, email, password))


def show_about_page():
    st.subheader('About')
    st.write('This application focuses on providing a credit report on a profile using a model implemented using pySurvival')
    st.write(
        'Application is developed by Bebeto Nyamwamu ')
    st.warning(
        'Warning! `Nuff said: To talk to your Data/Machine Learning Engineer at :email: [email](mailto:nberbetto@gmail.com) or view his works/profile on [Github](https://github.com/realonbebeto) or [Portfolio](http://realonbebeto.github.io/)')


def show_auth():
    login, register = st.tabs(["Login", "Register"])
    with login:
        show_login_page()
    with register:
        show_register_page()


def main():
    with headerSection:
        st.title("Finlytik: Credit Risk")
    # TODO: Future feature instead of loggedIn state, bearer token instead
    if 'loggedIn' not in st.session_state and 'token' not in st.session_state:
        st.session_state['token'] = None
        st.session_state['loggedIn'] = False
        show_auth()
    else:
        if st.session_state['loggedIn'] and st.session_state['token']:
            menu = ['Main', 'Reports', 'Logout', 'About']
            choice = st.sidebar.selectbox('Menu', menu)
            if choice == 'Main':
                show_main_page()
            elif choice == 'Reports':
                show_reports_page()
            elif choice == 'Logout':
                show_logout_page()
            elif choice == 'About':
                show_about_page()
        else:
            show_auth()


if __name__ == "__main__":
    try:
        main()
    except:
        st.error(
            'Oops! Something went wrong...Please check your input.\nIf you think there is a bug, please open up an [issue](https://github.com/realonbebeto/finSurvival/issues) and help us improve. ')
        raise
