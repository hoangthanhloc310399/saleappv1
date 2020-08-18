from flask import render_template, request, url_for, redirect, jsonify, send_file, session
from app import app, dao
from functools import wraps

# def login_required(f):
#     @wraps(f)
#     def check(*args, **kwargs):
#         if not session.get("user"):
#             return  redirect(url_for("login", next=request.url))
#
#         return f(*args, **kwargs)
#
#     return check()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/products")
def product_list():
    kw = request.args.get("keyword", None)
    from_price = request.args.get("from_price")
    to_price = request.args.get("to_price")
    return render_template("products.html",
                           products=dao.read_products(keyword=kw, from_price=from_price, to_price=to_price))


@app.route("/products/<int:category_id>")
def products_by_cate_id(category_id):
    return render_template("products.html",
                           products=dao.read_products(category_id=category_id))

@app.route("/products/add", methods=["get", "post"])
# @login_required
def add_or_update_pro():
    err = ""
    product_id = request.args.get("product_id")
    product = None
    if product_id:
        product = dao.read_product_by_id(product_id=int(product_id))

    if request.method.lower() == "post":
        # name = request.form.get("name")
        # price = request.form.get("price", 0)
        # images = request.form.get("images")
        # description = request.form.get("description")
        # category_id = request.form.get("category_id", 0)
        if product_id:
            data = dict(request.form.copy())
            data["product_id"] = product_id
            if dao.update_product(**data):
                return redirect(url_for("product_list"))
        else:
            if dao.add_products(**dict(request.form)):#name=name, price=price, images=images,description=description, category_id=category_id):
                return redirect(url_for("product_list"))

        err = "Someting Wrong"

    return render_template("product-add.html", categories= dao.read_categories(), product=product ,err=err)

@app.route("/api/products/<int:product_id>", methods=["delete"])
def delete_product(product_id):
    if dao.delete_product(product_id=product_id):
        return jsonify({
            "status": 200,
            "message": "Sucessful",
            "data": {"product_id": product_id}
        })
    return jsonify({
        "status": 500,
        "message": "Failed"
    })

@app.route("/products/export")
def export_product():
    return send_file(utils.export_csv())

@app.route("/login", methods=["get", "post"])
def login():
    err_msg = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = dao.validate_user(username=username, password=password)
        if user:
            session["user"] = user
            # if "next" in request.args:
            #     return redirect(request.args["next"])
            return redirect(url_for("index"))
        else:
            err_msg = "dang nhap sai"

    return render_template("Login.html", err_msg=err_msg)

@app.route("/logout")
def logout():
    session["user"] = None
    return redirect(url_for("index"))


@app.route("/register", methods=["get", "POST"])
def register():
    if session.get("user"):
        return redirect(request.url)


    err_msg = ""
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        user = dao.look_user(name=name)
        if user:
            err_msg = "Tên Này Đã Có Tài Khoản"
        else:
            if password.strip() != confirm.strip():
                err_msg = "Mật Khẩu Không Trùng Khớp"
            else:
                if dao.add_user(name=name, username=username, password=password):
                    return redirect(url_for("login"))
                else:
                    err_msg = "Something wrong !!!"


    return  render_template("register.html", err_msg= err_msg)

if __name__ == "__main__":
    app.run(debug=False)
