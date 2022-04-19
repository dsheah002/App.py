from flask import Flask, render_template, request, flash, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "Secret Key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql+pymysql://DevLogMaterialInventory_adm:JZul3IM/lvBSnS0@devux-db.sin.infineon.com:3306/DevLogMaterialInventory'
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

# Main page of mold
class MoldType(db.Model):
    __tablename__ = 'mold_types'

    mold_type_id = db.Column(db.Integer, primary_key=True)
    mold_name = db.Column(db.String(100))
    supplier = db.Column(db.String(100))
    pallet_size = db.Column(db.String(100))
    part_no = db.Column(db.String(100))
    weight = db.Column(db.String(100))

    mold_description = db.relationship("MoldDescription", cascade="all, delete-orphan")

    def __init__(self, mold_name, supplier, pallet_size, part_no, weight):
        self.mold_name = mold_name
        self.supplier = supplier
        self.pallet_size = pallet_size
        self.part_no = part_no
        self.weight = weight


# factors to classify the mold
class MoldDescription(db.Model):
    __tablename__ = 'mold_descriptions'

    mold_description_id = db.Column(db.Integer, primary_key=True)
    lot_no = db.Column(db.String(100))
    received_date = db.Column(db.String(100))
    expiry_date = db.Column(db.String(100))
    manufacturing_date= db.Column(db.String(100))
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
    mold_type_id = db.Column(db.Integer, db.ForeignKey('mold_types.mold_type_id'))

    mold_type = db.relationship("MoldType", backref='mold_type')

    def __init__(self, lot_no, received_date, expiry_date,manufacturing_date, project_leader, incoming_qty, withdraw_date, withdraw_qty,
                 withdraw_by, withdraw_purpose, balance, trans_type, release_status, expiry_status, created_time,
                 mold_type_id):
        self.lot_no = lot_no
        self.received_date = received_date
        self.expiry_date = expiry_date
        self.manufacturing_date = manufacturing_date
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
        self.mold_type_id = mold_type_id





db.create_all()
db.session.commit()


@app.route("/mold")
def show_mold():
    all_mold = db.session.query(MoldType, MoldDescription).join(MoldDescription).all()
    return render_template("mold.html", molds=all_mold)


@app.route("/mold_type")
def show_mold_types():
    all_mold_type = MoldType.query.order_by(MoldType.mold_type_id).all()
    return render_template("mold_type.html", mold_types=all_mold_type)


@app.route("/mold_type/<mold_type_id>")
def show_mold_descriptions(mold_type_id):
    all_mold_description = MoldDescription.query.filter_by(mold_type_id=mold_type_id). \
        order_by(MoldDescription.received_date.desc(), MoldDescription.created_time.desc(),
                 MoldDescription.withdraw_date).all()

    return render_template("mold_description.html",
                           mold_type=MoldType.query.filter_by(mold_type_id=mold_type_id).first(),
                           mold_descriptions=all_mold_description)


@app.route("/mold_type/insert", methods=['POST'])
def insert_mold_type():
    if request.method == 'POST':
        mold_name = request.form['mold_name']
        supplier = request.form['supplier']
        pallet_size = request.form['pallet_size']
        part_no = request.form['part_no']
        weight = request.form['weight']

        new_content = mold_name + ', ' + supplier + ', ' + pallet_size + ', ' + part_no + ', ' + weight
        new_mold_type = MoldType(mold_name, supplier, pallet_size, part_no, weight)

        db.session.add(new_mold_type)
        db.session.commit()
        flash("Mold type added successfully")

        new_edit = EditHistory(edit_type="Add", edit_material="Mold", edit_page="Transaction - mold type",
                               old_content="", new_content=new_content, changed_by=os.getlogin(),
                               changed_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.session.add(new_edit)
        db.session.commit()

    return redirect(url_for('show_mold_types'))


@app.route("/mold_description/insert/<mold_type_id>", methods=['POST'])
def insert_mold_description(mold_type_id):
    original_mold_type = MoldType.query.filter_by(mold_type_id=mold_type_id).first()
    if request.method == 'POST':
        lot_no = request.form['lot_no']
        received_date = request.form['received_date']
        expiry_date = request.form['expiry_date']
        manufacturing_date = request.form['manufacturing_date']
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

        new_content = '(Mold type)' + original_mold_type.mold_name + ', ' + lot_no + ', ' + received_date + ', ' \
                      + expiry_date + ', ' + manufacturing_date + ', ' + project_leader + ', ' + incoming_qty

        new_mold_description = MoldDescription(lot_no, received_date, expiry_date, manufacturing_date, project_leader, incoming_qty,
                                               withdraw_date, withdraw_by, withdraw_qty, withdraw_purpose, balance,
                                               trans_type, release_status, expiry_status, created_time,
                                               mold_type_id=mold_type_id)

        db.session.add(new_mold_description)
        db.session.commit()
        flash("Mold description added successfully")

        new_edit = EditHistory(edit_type="Add", edit_material="Mold", edit_page="Transaction - mold description",
                               old_content="", new_content=new_content, changed_by=os.getlogin(),
                               changed_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.session.add(new_edit)
        db.session.commit()

    return redirect(url_for('show_mold_descriptions', mold_type_id=mold_type_id))


@app.route('/mold_type/update', methods=['GET', 'POST'])
def update_mold_type():
    if request.method == 'POST':
        mold_type_to_update = MoldType.query.get(request.form.get('mold_type_id'))
        old_content = mold_type_to_update.mold_name + ', ' + mold_type_to_update.supplier + ', ' \
                      + mold_type_to_update.pallet_size + ', ' + mold_type_to_update.part_no + ', ' \
                      + mold_type_to_update.weight

        mold_type_to_update.mold_name = request.form['mold_name']
        mold_type_to_update.supplier = request.form['supplier']
        mold_type_to_update.pallet_size = request.form['pallet_size']
        mold_type_to_update.part_no = request.form['part_no']
        mold_type_to_update.weight = request.form['weight']

        db.session.commit()
        flash("Mold type [" + str(mold_type_to_update.mold_name) + "] is updated successfully")

        new_content = mold_type_to_update.mold_name + ', ' + mold_type_to_update.supplier + ', ' \
                      + mold_type_to_update.pallet_size + ', ' + mold_type_to_update.part_no + ', ' \
                      + mold_type_to_update.weight

        new_edit = EditHistory(edit_type="Update", edit_material="Mold", edit_page="Transaction - mold type",
                               old_content=old_content, new_content=new_content, changed_by=os.getlogin(),
                               changed_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.session.add(new_edit)
        db.session.commit()

        return redirect(url_for('show_mold_types'))


@app.route('/mold_description/update/<mold_description_id>', methods=['GET', 'POST'])
def update_mold_description(mold_description_id):
    if request.method == 'POST':
        mold_description_to_update = MoldDescription.query.filter_by(mold_description_id=mold_description_id).first()
        original_mold_type_id = mold_description_to_update.mold_type_id
        original_mold_type = MoldType.query.filter_by(mold_type_id=original_mold_type_id).first()

        old_content = '(Mold type)' + original_mold_type.mold_name + ', ' + mold_description_to_update.lot_no + ', ' \
                      + mold_description_to_update.received_date + ', ' \
                      + mold_description_to_update.expiry_date + ', ' + mold_description_to_update.manufacturing_date \
                      + mold_description_to_update.project_leader+ ', ' + mold_description_to_update.incoming_qty

        mold_description_to_update.lot_no = request.form['lot_no']
        mold_description_to_update.received_date = request.form['received_date']
        mold_description_to_update.expiry_date = request.form['expiry_date']
        mold_description_to_update.manufacturing_date = request.form['manufacturing_date']
        mold_description_to_update.project_leader = request.form['project_leader']
        mold_description_to_update.incoming_qty = request.form['incoming_qty']
        mold_description_to_update.balance = mold_description_to_update.incoming_qty

        db.session.commit()
        flash("Mold description for lot no. [" + str(mold_description_to_update.lot_no) + "] is updated successfully")

        new_content = '(Mold type)' + original_mold_type.mold_name + ', ' + mold_description_to_update.lot_no + ', ' \
                      + mold_description_to_update.received_date + ', ' + mold_description_to_update.expiry_date + ', '\
                      + mold_description_to_update.manufacturing_date + ', ' + mold_description_to_update.project_leader \
                      + ', ' + mold_description_to_update.incoming_qty

        new_edit = EditHistory(edit_type="Update", edit_material="Mold", edit_page="Transaction - mold description",
                               old_content=old_content, new_content=new_content, changed_by=os.getlogin(),
                               changed_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.session.add(new_edit)
        db.session.commit()

    return redirect(url_for('show_mold_descriptions', mold_type_id=original_mold_type_id))


@app.route('/mold_inventory/update/<mold_description_id>', methods=['GET', 'POST'])
def update_mold_inventory(mold_description_id):
    if request.method == 'POST':
        mold_to_update = MoldDescription.query.filter_by(mold_description_id=mold_description_id).first()
        original_mold_type_id = mold_to_update.mold_type_id
        original_mold_type = MoldType.query.filter_by(mold_type_id=original_mold_type_id).first()

        old_content = '(Mold type)' + original_mold_type.mold_name + ', (lot no.)' + mold_to_update.lot_no + ', ' \
                      + mold_to_update.balance + ', ' + mold_to_update.release_status

        mold_to_update.balance = request.form['balance']
        mold_to_update.release_status = request.form['release_status']

        db.session.commit()
        flash("Mold information for mold type [" + str(original_mold_type.mold_name) + "] and lot no. [" +
              str(mold_to_update.lot_no) + "] is updated successfully")

        new_content = '(Mold type)' + original_mold_type.mold_name + ', (lot no.)' + mold_to_update.lot_no + ', ' \
                      + mold_to_update.balance + ', ' + mold_to_update.release_status
        new_edit = EditHistory(edit_type="Update", edit_material="Mold", edit_page="Inventory",
                               old_content=old_content, new_content=new_content, changed_by=os.getlogin(),
                               changed_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.session.add(new_edit)
        db.session.commit()

    return redirect(url_for('show_mold'))


@app.route('/mold_description/withdraw/<mold_description_id>', methods=['GET', 'POST'])
def withdraw_mold_description(mold_description_id):
    if request.method == 'POST':
        mold_description_to_withdraw = MoldDescription.query.filter_by(mold_description_id=mold_description_id).first()
        original_mold_type_id = mold_description_to_withdraw.mold_type_id
        original_mold_type = MoldType.query.filter_by(mold_type_id=original_mold_type_id).first()

        new_mold_description = MoldDescription(lot_no=mold_description_to_withdraw.lot_no,
                                               received_date=mold_description_to_withdraw.received_date,
                                               expiry_date=mold_description_to_withdraw.expiry_date,
                                               manufacturing_date=mold_description_to_withdraw.manufacturing_date,
                                               project_leader=mold_description_to_withdraw.project_leader,
                                               incoming_qty=mold_description_to_withdraw.incoming_qty,
                                               withdraw_date=mold_description_to_withdraw.withdraw_date,
                                               withdraw_qty=mold_description_to_withdraw.withdraw_qty,
                                               withdraw_by=mold_description_to_withdraw.withdraw_by,
                                               withdraw_purpose=mold_description_to_withdraw.withdraw_purpose,
                                               balance=mold_description_to_withdraw.balance,
                                               trans_type=mold_description_to_withdraw.trans_type,
                                               release_status=mold_description_to_withdraw.release_status,
                                               expiry_status=mold_description_to_withdraw.expiry_status,
                                               created_time=mold_description_to_withdraw.created_time,
                                               mold_type_id=mold_description_to_withdraw.mold_type_id)

        new_mold_description.withdraw_date = request.form['withdraw_date']
        new_mold_description.withdraw_qty = request.form['withdraw_qty']
        new_mold_description.withdraw_by = request.form['withdraw_by']
        new_mold_description.withdraw_purpose = request.form['withdraw_purpose']
        new_mold_description.incoming_qty = ""
        new_mold_description.balance = ""
        new_mold_description.release_status = ""
        new_mold_description.expiry_status = ""
        new_mold_description.trans_type = "withdrawal"

        mold_description_to_withdraw.balance = \
            int(mold_description_to_withdraw.balance) - int(new_mold_description.withdraw_qty)

        if mold_description_to_withdraw.balance >= 0:
            db.session.add(new_mold_description)
            db.session.commit()
            flash("Mold withdrawal transaction added successfully")
        else:
            flash("Withdrawal failed. Balance cannot be negative", category="error")

        new_content = '(Mold type)' + original_mold_type.mold_name + ', ' + new_mold_description.lot_no + ', ' \
                      + new_mold_description.received_date + ', ' \
                      + new_mold_description.expiry_date + ', ' + + new_mold_description.manufacturing_date + ', ' \
                      + new_mold_description.project_leader + ', ' + new_mold_description.incoming_qty + ', ' \
                      + new_mold_description.withdraw_date + ', ' + new_mold_description.withdraw_qty + ', ' \
                      + new_mold_description.withdraw_by + ', ' + new_mold_description.withdraw_purpose

        new_edit = EditHistory(edit_type="Withdraw", edit_material="Mold", edit_page="Transaction - mold description",
                               old_content="", new_content=new_content, changed_by=os.getlogin(),
                               changed_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.session.add(new_edit)
        db.session.commit()

    return redirect(url_for('show_mold_descriptions', mold_type_id=original_mold_type_id))


@app.route("/mold_description/delete/<mold_description_id>", methods=['GET', 'POST'])
def delete_mold_description(mold_description_id):
    mold_description_to_delete = MoldDescription.query.filter_by(mold_description_id=mold_description_id).first()
    original_mold_type_id = mold_description_to_delete.mold_type.mold_type_id
    original_mold_type = MoldType.query.filter_by(mold_type_id=original_mold_type_id).first()

    if mold_description_to_delete.trans_type == "withdrawal":
        mold_description_to_update = MoldDescription.query.filter_by(
            lot_no=mold_description_to_delete.lot_no, received_date=mold_description_to_delete.received_date,
            trans_type="incoming").first()
        mold_description_to_update.balance = \
            int(mold_description_to_update.balance) + int(mold_description_to_delete.withdraw_qty)

        # edit history
        old_content = '(Mold type)' + original_mold_type.mold_name + ', ' + mold_description_to_delete.lot_no + ', ' \
                      + mold_description_to_delete.received_date + ', ' + mold_description_to_delete.expiry_date + ', ' \
                      + mold_description_to_delete.manufacturing_date + ', ' + mold_description_to_delete.project_leader+ ', ' \
                      + mold_description_to_delete.incoming_qty + ', ' + mold_description_to_delete.withdraw_date + ', ' \
                      + mold_description_to_delete.withdraw_qty + ', ' + mold_description_to_delete.withdraw_by \
                      + mold_description_to_delete.withdraw_purpose
        new_edit = EditHistory(edit_type="Delete", edit_material="Mold", edit_page="Transaction - mold description",
                               old_content=old_content, new_content="", changed_by=os.getlogin(),
                               changed_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.session.add(new_edit)

        db.session.delete(mold_description_to_delete)
        db.session.commit()
        flash("Withdrawal transaction deleted successfully")

    if mold_description_to_delete.trans_type == "incoming":
        mold_description_related = MoldDescription.query.filter_by(
            lot_no=mold_description_to_delete.lot_no, received_date=mold_description_to_delete.received_date).all()
        for m in mold_description_related:
            old_content = '(Mold type)' + original_mold_type.mold_name + ', ' + m.lot_no + ', ' + m.received_date \
                          + ', ' + m.expiry_date + ', ' + + ', ' + m.manufacturing_date + ', ' + m.project_leader + ', ' \
                          + m.incoming_qty + ', ' + m.withdraw_date + ', ' + m.withdraw_qty + ', ' + m.withdraw_by \
                          + ', ' + m.withdraw_purpose + ', ' + m.balance
            new_edit = EditHistory(edit_type="Delete", edit_material="Mold", edit_page="Transaction - mold description",
                                   old_content=old_content, new_content="", changed_by=os.getlogin(),
                                   changed_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            db.session.add(new_edit)

            db.session.delete(g)
        db.session.commit()
        flash("Incoming transaction and related withdrawal transactions are deleted successfully")

    return redirect(url_for('show_mold_descriptions', mold_type_id=original_mold_type_id))


@app.route("/mold_type/delete/<mold_type_id>", methods=['GET', 'POST'])
def delete_mold_type(mold_type_id):
    mold_type_to_delete = MoldType.query.filter_by(mold_type_id=mold_type_id).first()
    old_content = mold_type_to_delete.mold_name + ', ' + mold_type_to_delete.supplier + ', '\
                  + mold_type_to_delete.pallet_size + ', ' + mold_type_to_delete.part_no\
                  + ', ' + mold_type_to_delete.weight

    new_edit = EditHistory(edit_type="Delete", edit_material="Mold", edit_page="Transaction - mold type",
                           old_content=old_content, new_content="", changed_by=os.getlogin(),
                           changed_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    db.session.add(new_edit)
    db.session.commit()

    db.session.delete(mold_type_to_delete)
    db.session.commit()
    flash("Mold description deleted successfully")

    return redirect(url_for('show_mold_types'))




# Server configurations - REM CHANGE
# app.run(debug=True, host="api.ap-sg-1.icp.infineon.com", port=6443)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)
