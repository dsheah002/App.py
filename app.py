from flask import Flask, render_template, request, flash, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "Secret Key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = \
#     'mysql+pymysql://DevLogMaterialInventory_adm:JZul3IM/lvBSnS0@devux-db.sin.infineon.com:3306/DevLogMaterialInventory'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Main page of glue
class GlueType(db.Model):
    __tablename__ = 'glue_types'

    glue_type_id = db.Column(db.Integer, primary_key=True)
    glue_name = db.Column(db.String(100))
    supplier = db.Column(db.String(100))
    storage_temp = db.Column(db.String(100))
    freezer_no = db.Column(db.String(100))
    syringe_volume = db.Column(db.String(100))
    weight = db.Column(db.String(100))

    glue_description = db.relationship("GlueDescription", cascade="all, delete-orphan")

    def __init__(self, glue_name, supplier, storage_temp, freezer_no, syringe_volume, weight):
        self.glue_name = glue_name
        self.supplier = supplier
        self.storage_temp = storage_temp
        self.freezer_no = freezer_no
        self.syringe_volume = syringe_volume
        self.weight = weight


# factors to classify the glue
class GlueDescription(db.Model):
    __tablename__ = 'glue_descriptions'

    glue_description_id = db.Column(db.Integer, primary_key=True)
    lot_no = db.Column(db.String(100))
    received_date = db.Column(db.String(100))
    expiry_date = db.Column(db.String(100))
    project_leader = db.Column(db.String(100))
    incoming_qty = db.Column(db.String(100))
    withdraw_date = db.Column(db.String(100))
    withdraw_qty = db.Column(db.String(100))
    withdraw_by = db.Column(db.String(100))
    withdraw_purpose = db.Column(db.String(100))
    balance = db.Column(db.String(100))
    trans_type = db.Column(db.String(100))
    release_status = db.Column(db.String(100))
    expiry_status = db.Column(db.String(100))
    created_time = db.Column(db.DateTime, server_default=db.func.now())
    glue_type_id = db.Column(db.Integer, db.ForeignKey('glue_types.glue_type_id'))

    glue_type = db.relationship("GlueType", backref='glue_type')

    def __init__(self, lot_no, received_date, expiry_date, project_leader, incoming_qty, withdraw_date, withdraw_qty,
                 withdraw_by, withdraw_purpose, balance, trans_type, release_status, expiry_status, created_time,
                 glue_type_id):
        self.lot_no = lot_no
        self.received_date = received_date
        self.expiry_date = expiry_date
        self.project_leader = project_leader
        self.incoming_qty = incoming_qty
        self.withdraw_date = withdraw_date
        self.withdraw_qty = withdraw_qty
        self.withdraw_by = withdraw_by
        self.withdraw_purpose = withdraw_purpose
        self.balance = balance
        self.trans_type = trans_type
        self.release_status = release_status
        self.expiry_status = expiry_status
        self.created_time = created_time
        self.glue_type_id = glue_type_id


class EditHistory(db.Model):
    history_id = db.Column(db.Integer, primary_key=True)
    edit_type = db.Column(db.String(100))
    edit_material = db.Column(db.String(100))
    edit_page = db.Column(db.String(100))
    old_content = db.Column(db.String(200))
    new_content = db.Column(db.String(200))
    changed_by = db.Column(db.String(100))
    changed_time = db.Column(db.String(100))


db.create_all()
db.session.commit()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/history")
def show_history():
    all_history = EditHistory.query.order_by(EditHistory.changed_time.desc()).all()
    return render_template("history.html", histories=all_history)


@app.route("/glue")
def show_glue():
    all_glue = db.session.query(GlueType, GlueDescription).join(GlueDescription).all()
    return render_template("glue.html", glues=all_glue)


@app.route("/glue_type")
def show_glue_types():
    all_glue_type = GlueType.query.order_by(GlueType.glue_type_id).all()
    return render_template("glue_type.html", glue_types=all_glue_type)


@app.route("/glue_type/<glue_type_id>")
def show_glue_descriptions(glue_type_id):
    all_glue_description = GlueDescription.query.filter_by(glue_type_id=glue_type_id). \
        order_by(GlueDescription.received_date.desc(), GlueDescription.created_time.desc(),
                 GlueDescription.withdraw_date).all()

    return render_template("glue_description.html",
                           glue_type=GlueType.query.filter_by(glue_type_id=glue_type_id).first(),
                           glue_descriptions=all_glue_description)


@app.route("/glue_type/insert", methods=['POST'])
def insert_glue_type():
    if request.method == 'POST':
        glue_name = request.form['glue_name']
        supplier = request.form['supplier']
        storage_temp = request.form['storage_temp']
        freezer_no = request.form['freezer_no']
        syringe_volume = request.form['syringe_volume']
        weight = request.form['weight']

        new_content = glue_name + ', ' + supplier + ', ' + storage_temp + ', ' + freezer_no + ', ' + syringe_volume \
                      + ', ' + weight
        new_glue_type = GlueType(glue_name, supplier, storage_temp, freezer_no, syringe_volume, weight)

        db.session.add(new_glue_type)
        db.session.commit()
        flash("Glue type added successfully")

        new_edit = EditHistory(edit_type="Add", edit_material="Glue", edit_page="Transaction - glue type",
                               old_content="", new_content=new_content, changed_by=os.getlogin(),
                               changed_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.session.add(new_edit)
        db.session.commit()

    return redirect(url_for('show_glue_types'))


@app.route("/glue_description/insert/<glue_type_id>", methods=['POST'])
def insert_glue_description(glue_type_id):
    original_glue_type = GlueType.query.filter_by(glue_type_id=glue_type_id).first()
    if request.method == 'POST':
        lot_no = request.form['lot_no']
        received_date = request.form['received_date']
        expiry_date = request.form['expiry_date']
        project_leader = request.form['project_leader']
        incoming_qty = request.form['incoming_qty']
        withdraw_date = ""
        withdraw_qty = ""
        withdraw_by = ""
        withdraw_purpose = ""
        balance = incoming_qty
        trans_type = "incoming"
        release_status = ""
        expiry_status = ""
        created_time = datetime.now()

        new_content = '(Glue type)' + original_glue_type.glue_name + ', ' + lot_no + ', ' + received_date + ', ' \
                      + expiry_date + ', ' + project_leader + ', ' + incoming_qty

        new_glue_description = GlueDescription(lot_no, received_date, expiry_date, project_leader, incoming_qty,
                                               withdraw_date, withdraw_by, withdraw_qty, withdraw_purpose, balance,
                                               trans_type, release_status, expiry_status, created_time,
                                               glue_type_id=glue_type_id)

        db.session.add(new_glue_description)
        db.session.commit()
        flash("Glue description added successfully")

        new_edit = EditHistory(edit_type="Add", edit_material="Glue", edit_page="Transaction - glue description",
                               old_content="", new_content=new_content, changed_by=os.getlogin(),
                               changed_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.session.add(new_edit)
        db.session.commit()

    return redirect(url_for('show_glue_descriptions', glue_type_id=glue_type_id))


@app.route('/glue_type/update', methods=['GET', 'POST'])
def update_glue_type():
    if request.method == 'POST':
        glue_type_to_update = GlueType.query.get(request.form.get('glue_type_id'))
        old_content = glue_type_to_update.glue_name + ', ' + glue_type_to_update.supplier + ', ' \
                      + glue_type_to_update.storage_temp + ', ' + glue_type_to_update.freezer_no + ', ' \
                      + glue_type_to_update.syringe_volume + ', ' + glue_type_to_update.weight

        glue_type_to_update.glue_name = request.form['glue_name']
        glue_type_to_update.supplier = request.form['supplier']
        glue_type_to_update.storage_temp = request.form['storage_temp']
        glue_type_to_update.freezer_no = request.form['freezer_no']
        glue_type_to_update.syringe_volume = request.form['syringe_volume']
        glue_type_to_update.weight = request.form['weight']

        db.session.commit()
        flash("Glue type [" + str(glue_type_to_update.glue_name) + "] is updated successfully")

        new_content = glue_type_to_update.glue_name + ', ' + glue_type_to_update.supplier + ', ' \
                      + glue_type_to_update.storage_temp + ', ' + glue_type_to_update.freezer_no + ', ' \
                      + glue_type_to_update.syringe_volume + ', ' + glue_type_to_update.weight

        new_edit = EditHistory(edit_type="Update", edit_material="Glue", edit_page="Transaction - glue type",
                               old_content=old_content, new_content=new_content, changed_by=os.getlogin(),
                               changed_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.session.add(new_edit)
        db.session.commit()

        return redirect(url_for('show_glue_types'))


@app.route('/glue_description/update/<glue_description_id>', methods=['GET', 'POST'])
def update_glue_description(glue_description_id):
    if request.method == 'POST':
        glue_description_to_update = GlueDescription.query.filter_by(glue_description_id=glue_description_id).first()
        original_glue_type_id = glue_description_to_update.glue_type_id
        original_glue_type = GlueType.query.filter_by(glue_type_id=original_glue_type_id).first()

        old_content = '(Glue type)' + original_glue_type.glue_name + ', ' + glue_description_to_update.lot_no + ', ' \
                      + glue_description_to_update.received_date + ', ' \
                      + glue_description_to_update.expiry_date + ', ' + glue_description_to_update.project_leader \
                      + ', ' + glue_description_to_update.incoming_qty

        glue_description_to_update.lot_no = request.form['lot_no']
        glue_description_to_update.received_date = request.form['received_date']
        glue_description_to_update.expiry_date = request.form['expiry_date']
        glue_description_to_update.project_leader = request.form['project_leader']
        glue_description_to_update.incoming_qty = request.form['incoming_qty']
        glue_description_to_update.balance = glue_description_to_update.incoming_qty

        db.session.commit()
        flash("Glue description for lot no. [" + str(glue_description_to_update.lot_no) + "] is updated successfully")

        new_content = '(Glue type)' + original_glue_type.glue_name + ', ' + glue_description_to_update.lot_no + ', ' \
                      + glue_description_to_update.received_date + ', ' \
                      + glue_description_to_update.expiry_date + ', ' + glue_description_to_update.project_leader \
                      + ', ' + glue_description_to_update.incoming_qty

        new_edit = EditHistory(edit_type="Update", edit_material="Glue", edit_page="Transaction - glue description",
                               old_content=old_content, new_content=new_content, changed_by=os.getlogin(),
                               changed_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.session.add(new_edit)
        db.session.commit()

    return redirect(url_for('show_glue_descriptions', glue_type_id=original_glue_type_id))


@app.route('/glue_inventory/update/<glue_description_id>', methods=['GET', 'POST'])
def update_glue_inventory(glue_description_id):
    if request.method == 'POST':
        glue_to_update = GlueDescription.query.filter_by(glue_description_id=glue_description_id).first()
        original_glue_type_id = glue_to_update.glue_type_id
        original_glue_type = GlueType.query.filter_by(glue_type_id=original_glue_type_id).first()

        old_content = '(Glue type)' + original_glue_type.glue_name + ', (lot no.)' + glue_to_update.lot_no + ', ' \
                      + glue_to_update.balance + ', ' + glue_to_update.release_status

        glue_to_update.balance = request.form['balance']
        glue_to_update.release_status = request.form['release_status']

        db.session.commit()
        flash("Glue information for glue type [" + str(original_glue_type.glue_name) + "] and lot no. [" +
              str(glue_to_update.lot_no) + "] is updated successfully")

        new_content = '(Glue type)' + original_glue_type.glue_name + ', (lot no.)' + glue_to_update.lot_no + ', ' \
                      + glue_to_update.balance + ', ' + glue_to_update.release_status
        new_edit = EditHistory(edit_type="Update", edit_material="Glue", edit_page="Inventory",
                               old_content=old_content, new_content=new_content, changed_by=os.getlogin(),
                               changed_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.session.add(new_edit)
        db.session.commit()

    return redirect(url_for('show_glue'))


@app.route('/glue_description/withdraw/<glue_description_id>', methods=['GET', 'POST'])
def withdraw_glue_description(glue_description_id):
    if request.method == 'POST':
        glue_description_to_withdraw = GlueDescription.query.filter_by(glue_description_id=glue_description_id).first()
        original_glue_type_id = glue_description_to_withdraw.glue_type_id
        original_glue_type = GlueType.query.filter_by(glue_type_id=original_glue_type_id).first()

        new_glue_description = GlueDescription(lot_no=glue_description_to_withdraw.lot_no,
                                               received_date=glue_description_to_withdraw.received_date,
                                               expiry_date=glue_description_to_withdraw.expiry_date,
                                               project_leader=glue_description_to_withdraw.project_leader,
                                               incoming_qty=glue_description_to_withdraw.incoming_qty,
                                               withdraw_date=glue_description_to_withdraw.withdraw_date,
                                               withdraw_qty=glue_description_to_withdraw.withdraw_qty,
                                               withdraw_by=glue_description_to_withdraw.withdraw_by,
                                               withdraw_purpose=glue_description_to_withdraw.withdraw_purpose,
                                               balance=glue_description_to_withdraw.balance,
                                               trans_type=glue_description_to_withdraw.trans_type,
                                               release_status=glue_description_to_withdraw.release_status,
                                               expiry_status=glue_description_to_withdraw.expiry_status,
                                               created_time=glue_description_to_withdraw.created_time,
                                               glue_type_id=glue_description_to_withdraw.glue_type_id)

        new_glue_description.withdraw_date = request.form['withdraw_date']
        new_glue_description.withdraw_qty = request.form['withdraw_qty']
        new_glue_description.withdraw_by = request.form['withdraw_by']
        new_glue_description.withdraw_purpose = request.form['withdraw_purpose']
        new_glue_description.incoming_qty = ""
        new_glue_description.balance = ""
        new_glue_description.release_status = ""
        new_glue_description.expiry_status = ""
        new_glue_description.trans_type = "withdrawal"

        glue_description_to_withdraw.balance = \
            int(glue_description_to_withdraw.balance) - int(new_glue_description.withdraw_qty)

        if glue_description_to_withdraw.balance >= 0:
            db.session.add(new_glue_description)
            db.session.commit()
            flash("Glue withdrawal transaction added successfully")
        else:
            flash("Withdrawal failed. Balance cannot be negative", category="error")

        new_content = '(Glue type)' + original_glue_type.glue_name + ', ' + new_glue_description.lot_no + ', ' \
                      + new_glue_description.received_date + ', ' \
                      + new_glue_description.expiry_date + ', ' + new_glue_description.project_leader + ', ' \
                      + new_glue_description.incoming_qty + ', ' + new_glue_description.withdraw_date + ', ' \
                      + new_glue_description.withdraw_qty + ', ' + new_glue_description.withdraw_by + ', ' \
                      + new_glue_description.withdraw_purpose

        new_edit = EditHistory(edit_type="Withdraw", edit_material="Glue", edit_page="Transaction - glue description",
                               old_content="", new_content=new_content, changed_by=os.getlogin(),
                               changed_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.session.add(new_edit)
        db.session.commit()

    return redirect(url_for('show_glue_descriptions', glue_type_id=original_glue_type_id))


@app.route("/glue_description/delete/<glue_description_id>", methods=['GET', 'POST'])
def delete_glue_description(glue_description_id):
    glue_description_to_delete = GlueDescription.query.filter_by(glue_description_id=glue_description_id).first()
    original_glue_type_id = glue_description_to_delete.glue_type.glue_type_id
    original_glue_type = GlueType.query.filter_by(glue_type_id=original_glue_type_id).first()

    if glue_description_to_delete.trans_type == "withdrawal":
        glue_description_to_update = GlueDescription.query.filter_by(
            lot_no=glue_description_to_delete.lot_no, received_date=glue_description_to_delete.received_date,
            trans_type="incoming").first()
        glue_description_to_update.balance = \
            int(glue_description_to_update.balance) + int(glue_description_to_delete.withdraw_qty)

        # edit history
        old_content = '(Glue type)' + original_glue_type.glue_name + ', ' + glue_description_to_delete.lot_no + ', ' + glue_description_to_delete.received_date + ', ' \
                      + glue_description_to_delete.expiry_date + ', ' + glue_description_to_delete.project_leader \
                      + ', ' + glue_description_to_delete.incoming_qty + ', ' \
                      + glue_description_to_delete.withdraw_date + ', ' + glue_description_to_delete.withdraw_qty \
                      + ', ' + glue_description_to_delete.withdraw_by + ', ' \
                      + glue_description_to_delete.withdraw_purpose
        new_edit = EditHistory(edit_type="Delete", edit_material="Glue", edit_page="Transaction - glue description",
                               old_content=old_content, new_content="", changed_by=os.getlogin(),
                               changed_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.session.add(new_edit)

        db.session.delete(glue_description_to_delete)
        db.session.commit()
        flash("Withdrawal transaction deleted successfully")

    if glue_description_to_delete.trans_type == "incoming":
        glue_description_related = GlueDescription.query.filter_by(
            lot_no=glue_description_to_delete.lot_no, received_date=glue_description_to_delete.received_date).all()
        for g in glue_description_related:
            old_content = '(Glue type)' + original_glue_type.glue_name + ', ' + g.lot_no + ', ' + g.received_date \
                          + ', ' + g.expiry_date + ', ' + g.project_leader + ', ' \
                          + g.incoming_qty + ', ' + g.withdraw_date + ', ' + g.withdraw_qty + ', ' + g.withdraw_by \
                          + ', ' + g.withdraw_purpose + ', ' + g.balance
            new_edit = EditHistory(edit_type="Delete", edit_material="Glue", edit_page="Transaction - glue description",
                                   old_content=old_content, new_content="", changed_by=os.getlogin(),
                                   changed_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            db.session.add(new_edit)

            db.session.delete(g)
        db.session.commit()
        flash("Incoming transaction and related withdrawal transactions are deleted successfully")

    return redirect(url_for('show_glue_descriptions', glue_type_id=original_glue_type_id))


@app.route("/glue_type/delete/<glue_type_id>", methods=['GET', 'POST'])
def delete_glue_type(glue_type_id):
    glue_type_to_delete = GlueType.query.filter_by(glue_type_id=glue_type_id).first()
    old_content = glue_type_to_delete.glue_name + ', ' + glue_type_to_delete.supplier + ', '\
                  + glue_type_to_delete.storage_temp + ', ' + glue_type_to_delete.freezer_no\
                  + ', ' + glue_type_to_delete.syringe_volume + ', ' + glue_type_to_delete.weight

    new_edit = EditHistory(edit_type="Delete", edit_material="Glue", edit_page="Transaction - glue type",
                           old_content=old_content, new_content="", changed_by=os.getlogin(),
                           changed_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    db.session.add(new_edit)
    db.session.commit()

    db.session.delete(glue_type_to_delete)
    db.session.commit()
    flash("Glue description deleted successfully")

    return redirect(url_for('show_glue_types'))


# Server configurations - REM CHANGE
# app.run(debug=True, host="api.ap-sg-1.icp.infineon.com", port=6443)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)
