# Create a user in your db with the information provided
# by Google
user = User(
    id_=unique_id, name=users_name, email=users_email, profile_pic=picture
)

# Doesn't exist? Add it to the database.
if not User.get(unique_id):
    User.create(unique_id, users_name, users_email, picture)

# Begin user session by logging the user in
login_user(user)

# Send user back to homepage
return redirect(url_for("index"))