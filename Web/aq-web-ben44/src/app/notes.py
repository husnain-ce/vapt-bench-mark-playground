from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import Document
from .auth import access_required
from . import db


workspace_bp = Blueprint('workspace', __name__)

@workspace_bp.route('/home')
@access_required
def home():
    account_id = session['account_id']
    documents = Document.query.filter_by(owner_id=account_id).order_by(Document.created_time.desc()).all()
    return render_template('workspace/home.html', documents=documents)

@workspace_bp.route('/compose', methods=['GET', 'POST'])
@access_required
def compose_document():
    if request.method == 'POST':
        heading = request.form['title']
        body = request.form['content']
        
        if not heading or not body:
            flash('Heading and content are required!', 'error')
            return render_template('workspace/compose.html')
        
        document = Document(
            heading=heading,
            body=body,
            owner_id=session['account_id']
        )
        db.session.add(document)
        db.session.commit()

        # redirect to the document
        
        flash('Document created successfully!', 'success')
        return redirect('/workspace/display/' + document.id)
    
    return render_template('workspace/compose.html')

@workspace_bp.route('/modify/<string:doc_id>', methods=['GET', 'POST'])
@access_required
def modify_document(doc_id):
    document = Document.query.get_or_404(doc_id)
    
    # Check if user owns this document
    if document.owner_id != session['account_id']:
        flash('You can only modify your own documents!', 'error')
        return redirect(url_for('workspace.home'))
    
    if request.method == 'POST':
        heading = request.form['title']
        body = request.form['content']
        
        if not heading or not body:
            flash('Heading and content are required!', 'error')
            return render_template('workspace/modify.html', document=document)
        
        document.heading = heading
        document.body = body
        db.session.commit()
        
        flash('Document updated successfully!', 'success')
        return redirect(url_for('workspace.home'))
    
    return render_template('workspace/modify.html', document=document)

@workspace_bp.route('/display/<string:doc_id>')
@access_required
def display_document(doc_id):
    document = Document.query.get_or_404(doc_id)
    
    return render_template('workspace/display.html', document=document)

@workspace_bp.route('/remove/<string:doc_id>', methods=['POST'])
@access_required
def remove_document(doc_id):
    document = Document.query.get_or_404(doc_id)

    if session.get('has_admin_rights') or document.owner_id == session['account_id']:
        db.session.delete(document)
        db.session.commit()
        flash('Document deleted successfully!', 'success')
    else:
        flash('You can only delete your own documents!', 'error')
    return redirect(url_for('workspace.home'))
