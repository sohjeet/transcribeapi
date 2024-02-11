import click
from app.db import models
from app.db.database import SessionLocal
from users import create_hashed_password                       
from email_validator import validate_email, EmailNotValidError

def is_valid_email(ctx, param, value):
    # Custom click option validation for email
    try:
        validate_email(value)
        return value
    except EmailNotValidError:
        raise click.BadParameter('Invalid email address')

def validate_password(ctx, param, value):
    # Custom click option validation for password
    if len(value) < 7:
        raise click.BadParameter('Password must be at least 7 characters long')
    if value != click.prompt('Confirm Password', hide_input=True):
        raise click.BadParameter('Passwords do not match')
    return value

def is_admin_exists(username: str):
    # Check if an admin exists
    with SessionLocal() as db:
        user =  db.query(models.User).filter_by(username=username, is_admin=True).first()
    return user

def is_email_exists(email: str):
    # Check if an email exists
    with SessionLocal() as db:
        email_exists =  db.query(models.User).filter_by(email=email).first()
    if email_exists:
        return True
    return False

def echo_success(message):
    click.echo(click.style(message, fg='green'))

def echo_failure(message):
    click.echo(click.style(message, fg='red'))

@click.group()
def cli():
    pass

@cli.command()
@click.option('--email', prompt='Email', type=str, callback=is_valid_email)
@click.option('--username', prompt='Username', type=str)
@click.option('--password', prompt='Password', hide_input=True, type=str, callback=validate_password)
def create_admin(email, username, password):
    if is_admin_exists(username) or is_email_exists(email):
        echo_failure(f"Admin '{username}' already exists. Please use a different username or email.")
        return
    hashed_password = create_hashed_password(plaintext_password=password)
    update_password = hashed_password
      
    # Create a new super admin
    super_admin = models.User(
        email=email,
        username=username,
        password=update_password,
        is_admin=True,
        is_superuser=True,
    )
    with SessionLocal() as db:
        db.add(super_admin)
        db.commit()

    echo_success(f"Admin '{username}' created successfully.")

@cli.command()
@click.option('--username', prompt='Username', type=str)
@click.option('--new_password', prompt='New Password', hide_input=True, type=str, callback=validate_password)
def change_admin_password(username, new_password):
    with SessionLocal() as db:
        # Find the admin by username
        admin = is_admin_exists(username)
        if admin:
            # Update the admin's password
            admin.password =  create_hashed_password(plaintext_password=new_password)
            try:
                db.commit()
                echo_success(f"Password for admin '{username}' changed successfully.")
            except Exception as e:
                db.rollback()
                echo_failure(f"Error changing password: {str(e)}")
        else:
            echo_failure(f"Admin '{username}' not found.")

@cli.command()
@click.option('--username', prompt='Username', type=str)
@click.option('--new_email', prompt='New Email', type=str, callback=is_valid_email)
def change_admin_email(username, new_email):
    with  SessionLocal() as db:
        # Find the admin by username
        admin = is_admin_exists(username)
        email = is_email_exists(new_email)
        if admin:
            if email:
                echo_failure(f"Email '{new_email}' already exists. Please use a different email.")
                return
            # Update the admin's email
            admin.email = new_email
            try:
                db.commit()
                echo_success(f"Email for admin '{username}' changed successfully.")
            except Exception as e:
                db.rollback()
                echo_failure(f"Error changing email: {str(e)}")
        else:
            echo_failure(f"Admin '{username}' not found.")

if __name__ == '__main__':
    cli()
