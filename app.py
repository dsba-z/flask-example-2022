from flask import Flask
from flask import render_template
from flask import send_file
from flask import request

app = Flask(__name__)


links = {
    "Download": "/download",
    "Raw data": "/raw_data",
    "Pairplot": "/pairplot",
    "Fair vs Pclass": "/fair_vs_pclass",
    "PClass vs Sex": "/pclass_vs_sex",
    "Passengers": "/passenges",
    "View Raw Data": "/view_data",
}


def render_index(image=None, html_string=None, filters=None, errors=None, current_filter_value=""):
    return render_template(
        "index.html",
        links=links,
        image=image,
        html_string=html_string,
        filters=filters,
        errors=errors,
        current_filter_value=current_filter_value,
    )


@app.route("/", methods=["GET"])
def home_page():
    return render_index()


@app.route(links["Download"], methods=["GET"])
def download_data():
    return send_file("titanic_train.csv", as_attachment=True)


@app.route(links["Pairplot"], methods=["GET"])
def pairplot():
    import seaborn as sns
    import pandas as pd

    data = pd.read_csv("data/titanic_train.csv")
    sns_plot = sns.pairplot(data, hue="Survived")
    sns_plot.savefig("static/tmp/pairplot.png")
    return render_index(image="pairplot.png")


@app.route(links["Fair vs Pclass"], methods=["GET"])
def fair_vs_pclass():
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns

    sns.set_theme()

    data = pd.read_csv("data/titanic_train.csv")
    filtered_data = data.query("Fare < 200")
    sns.boxplot(x="Pclass", y="Fare", data=filtered_data)
    plt.savefig("static/tmp/fair_vs_pclass.png")

    return render_index(image="fair_vs_pclass.png")


@app.route(links["PClass vs Sex"], methods=["GET"])
def pclass_vs_sex():
    import matplotlib.pyplot as plt
    import pandas as pd

    data = pd.read_csv("data/titanic_train.csv")
    result = {}
    for (cl, sex), sub_df in data.groupby(["Pclass", "Sex"]):
        result[f"{cl} {sex}"] = sub_df["Age"].mean()

    plt.bar(result.keys(), result.values())
    plt.savefig("static/pclass_vs_sex.png")
    return render_index(image="pclass_vs_sex.png")


@app.route(links["View Raw Data"], methods=["GET", "POST"])
def raw_data():
    import pandas as pd

    errors = []
    df = pd.read_csv("data/titanic_train.csv")
    current_filter_value = ""
    if request.method == "POST":
        current_filter = request.form.get("filters")
        current_filter_value = current_filter
        if current_filter:
            try:
                df = df.query(current_filter)
            except Exception as e:
                errors.append('<font color="red">Incorrect filter</font>')
                print(e)

    page = df.to_html()

    return render_index(html_string=page, filters=True, errors=errors, current_filter_value=current_filter_value)


@app.route(links["Passengers"], methods=['GET', 'POST'])
def passengers():

    import pandas as pd
    df = pd.read_csv("data/titanic_train.csv")
    errors = []
    current_filter_value = ""
    if request.method == "POST":
        current_filter = request.form.get('filters')
        current_filter_value = current_filter
        if current_filter:
            try:
                df = df.query(current_filter)
            except Exception as e:
                errors.append('<font color="red">Incorrect filter</font>')
                print(e)

    passengers = list(df["Name"].unique())
    text = "<br/>".join(passengers)
    return render_index(html_string=text, filters=True, errors=errors, current_filter_value=current_filter_value)


app.run(port=5001)
