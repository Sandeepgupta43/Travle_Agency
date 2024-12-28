
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.secret_key = '1234'

# Configure MySQL DB connection
#                                        mysql+pymysql://username:password@localhost/database_name
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ums08mncjhlpb9cj:A5pr1lVIVqR2t0Uv2N7G@bgpvzgqi3qve3lyjqkzs-mysql.services.clever-cloud.com:3306/bgpvzgqi3qve3lyjqkzs'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MySQL Database Models
class User(db.Model):
    __tablename__ = 'users'  # Table name in MySQL
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(15))
    is_admin = db.Column(db.Boolean,default=False)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_type = db.Column(db.String(20), nullable=False)
    transport_id = db.Column(db.Integer,nullable=False)
    passenger_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    amount = db.Column(db.Float, nullable=False)

    status = db.Column(db.String(20), default='Not confirm')

class Flight(db.Model):
    __tablename__ = 'flights'
    id = db.Column(db.Integer, primary_key=True)
    flight_name = db.Column(db.String(100), nullable=False)
    from_location = db.Column(db.String(100), nullable=False)
    to_location = db.Column(db.String(100), nullable=False)
    departure_date = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    seats = db.Column(db.Integer, nullable=False)

class Railway(db.Model):
    __tablename__ = 'railways'
    id = db.Column(db.Integer, primary_key=True)
    train_name = db.Column(db.String(100), nullable=False)
    from_location = db.Column(db.String(100), nullable=False)
    to_location = db.Column(db.String(100), nullable=False)
    departure_date = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    seats = db.Column(db.Integer, nullable=False)

class Bus(db.Model):
    __tablename__ = 'buses'
    id = db.Column(db.Integer, primary_key=True)
    bus_name = db.Column(db.String(100), nullable=False)
    from_location = db.Column(db.String(100), nullable=False)
    to_location = db.Column(db.String(100), nullable=False)
    departure_date = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    seats = db.Column(db.Integer, nullable=False)


class Hotel(db.Model):
    __tablename__ = 'hotels'
    id = db.Column(db.Integer, primary_key=True)
    hotel_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)
    room = db.Column(db.Integer, nullable=False)

class Passenger(db.Model):
    __tablename__ = 'passengers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transport_id = db.Column(db.Integer, nullable=False)
    booking_type = db.Column(db.String(15), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone_no = db.Column(db.String(15), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    seat_number = db.Column(db.Integer, nullable=False)

# Routes
@app.route('/')
def home():
    return render_template('home.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        contact_number = request.form['contact_number']


        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            if existing_user.username == username:
                flash('Username already exists!', 'error')
            if existing_user.email == email:
                flash('Email already exists!', 'error')
            return redirect(url_for('register'))


        # Add user to DB
        new_user = User(username=username, email=email, password=password, contact_number=contact_number)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration Successful! Please log in.','success')
        return redirect(url_for('login'))
    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            if user.is_admin:
                flash('Login successful!', 'success')  # Success message
                return redirect(url_for('admin_dashboard'))
            else:

                return redirect(url_for('dashboard'))
        else:

            flash('Invalid username or password!', 'error')  # Error message
            return render_template('login.html')
    return render_template('login.html')

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash('You need to log in to access this page.', 'danger')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        email = request.form.get('email')
        contact_number = request.form.get('contact_number')

        # Validate and update the user's information
        if username:
            user.username = username
        if email:
            if User.query.filter(User.email == email, User.id != user.id).first():
                flash('Email is already in use.', 'danger')
                return render_template('edit_profile.html', user=user)
            user.email = email
        if contact_number:
            user.contact_number = contact_number

        # Commit changes
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))  # Redirect back to the dashboard

    return render_template('edit_profile.html', user=user)

@app.route('/forget', methods=['GET', 'POST'])
def forget():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:

            session['reset_user_id'] = user.id
            return redirect(url_for('reset_password'))
        else:
            flash('No account found with that email.', 'error')
    return render_template('forget_password.html')


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_user_id' not in session:
        flash('Unauthorized access. Please try again.', 'error')
        return redirect(url_for('forget'))

    if request.method == 'POST':
        password = request.form['password']
        user_id = session['reset_user_id']

        user = User.query.get(user_id)
        if user:
            user.password = password
            db.session.commit()

            session.pop('reset_user_id', None)
            flash('Password has been reset successfully!', 'success')
            return redirect(url_for('login'))

    return render_template('reset_password.html')


@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if not user.is_admin:
        return redirect(url_for('home'))  # Only allow admin access

    # Fetch all users and bookings
    users = User.query.all()
    bookings = Booking.query.all()

    return render_template('admin_dashboard.html', users=users, bookings=bookings)



@app.route('/all_bookings',methods=['GET'])
def all_bookings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        return redirect(url_for('home'))
    bookings = Booking.query.all()
    return render_template('all_bookings.html', bookings=bookings)



@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    booking_details = Booking.query.filter_by(user_id=session['user_id']).all()
    if user.is_admin:
        return redirect(url_for('admin_dashboard'))  # Redirect admin to the admin dashboard

    return render_template('dashboard.html', user=user,booking_details=booking_details)


# this for booking details
@app.route('/dashboard/details')
def details():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    booking_id = request.args.get('booking_id')
    passenger_id = request.args.get('passenger_id')

    # Validate query parameters
    if not booking_id or not passenger_id:
        flash("Booking ID or Passenger ID is missing.")
        return redirect(url_for('dashboard'))

    # Fetch the booking
    booking = Booking.query.filter_by(id=booking_id, user_id=session['user_id']).first()
    if not booking:
        flash("Booking not found.")
        return redirect(url_for('dashboard'))

    # Fetch passenger details
    passenger = Passenger.query.filter_by(transport_id=booking.transport_id, id=passenger_id).first()
    if not passenger:
        flash("Passenger details not found.")
        return redirect(url_for('dashboard'))

    # Initialize default values
    hotel_location = None
    room_number = None
    from_location = None
    to_location = None
    departure_date = None

    # Fetch transport/hotel details based on booking type
    if booking.booking_type == 'flight':
        transport = Flight.query.get(booking.transport_id)
    elif booking.booking_type == 'train':
        transport = Railway.query.get(booking.transport_id)
    elif booking.booking_type == 'bus':
        transport = Bus.query.get(booking.transport_id)
    elif booking.booking_type == 'hotel':
        transport = Hotel.query.get(booking.transport_id)
    else:
        flash("Invalid booking type.")
        return redirect(url_for('dashboard'))

    # Handle transport or hotel details
    if transport:
        if booking.booking_type == 'hotel':
            room_number = 1  # Default room number or logic to calculate it
            hotel_location = transport.location
        else:
            from_location = transport.from_location
            to_location = transport.to_location
            departure_date = transport.departure_date
    else:
        flash("Transport or hotel details not found.")
        return redirect(url_for('dashboard'))

    # Pass data to the template
    return render_template(
        'details.html',
        booking=booking,
        first_passenger=passenger,
        from_location=from_location,
        to_location=to_location,
        departure_date=departure_date,
        room_number=room_number,
        hotel_location=hotel_location
    )





valid_coupons = {
    "CRIS2024": 15,  # 15% off
    "DISCOUNT2024": 10,  # 10% off
    # Add more coupons here
}

@app.route('/verifyCoupon', methods=['POST'])
def verify_coupon():
    data = request.get_json()
    coupon_code = data.get('coupon')

    if coupon_code in valid_coupons:
        return jsonify({"valid": True, "discount": valid_coupons[coupon_code]})
    else:
        return jsonify({"valid": False})

# This is for flight
@app.route('/flight',methods=['GET','POST'])
def flight():

    return render_template('flight.html')

# for search flight
@app.route('/flight/search_flight',methods=['POST'])
def search_flight():
    from_location = request.form['from_location'].replace(" ","").lower()
    to_location = request.form['to_location'].replace(" ","").lower()
    departure_date = request.form['departure_date']

    # Filter the database using case-insensitive and whitespace-ignored comparisons
    flights = Flight.query.filter(
        func.replace(func.lower(Flight.from_location), " ", "") == from_location,
        func.replace(func.lower(Flight.to_location), " ", "") == to_location,
        func.date(Flight.departure_date) == departure_date
    ).all()
    return render_template('flight_results.html',flights=flights)

# Show all flights on admin pannel
@app.route('/admin/flights',methods=['GET'])
def all_flights():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to acces this page.')
        return redirect(url_for('dashboard'))
    flights = Flight.query.all()
    return render_template('all_flights.html',flights=flights)


# for adding new flight
@app.route('/admin/addFlight',methods=['GET','POST'])
def add_flight():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to acces this page.')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        flight_name = request.form['flight_name']
        from_location = request.form['from_location']
        to_location = request.form['to_location']
        departure_date = request.form['departure_date']
        seats = request.form['seats']
        price = request.form['price']
        new_flight = Flight(flight_name=flight_name,from_location=from_location,to_location=to_location,departure_date=departure_date,price=price,seats=seats)
        db.session.add(new_flight)
        db.session.commit()
        flash('Flight is added')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_flight.html')


# for editing flight details
@app.route('/admin/edit_flight/<int:flight_id>',methods=['GET','POST'])
def edit_flight(flight_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to acces this page.')
        return redirect(url_for('dashboard'))
    flight = Flight.query.get(flight_id)
    if request.method == 'POST':
        flight.flight_name = request.form['flight_name']
        flight.from_location = request.form['from_location']
        flight.to_location = request.form['to_location']
        flight.departure_date = request.form['departure_date']
        flight.price = request.form['price']
        flight.seats = request.form['seats']
        db.session.commit()
        flash('Flight details updated')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_flight.html',flight=flight)

# for delete a flight
@app.route('/admin/delete_flight',methods=['POST'])
def delete_flight():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to acces this page.')
        return redirect(url_for('dashboard'))
    flight_id = request.form['flight_id']
    flight = Flight.query.get(flight_id)

    db.session.delete(flight)
    db.session.commit()
    flash('Flight deleted successfully')
    return redirect(url_for('admin_dashboard'))

# This is for railway
@app.route('/railway',methods=['GET','POST'])
def railway():


    return render_template('railway.html')


# for search train
@app.route('/railway/search_train',methods=['POST'])
def search_train():
    from_location = request.form['from_location'].replace(" ","").lower()
    to_location = request.form['to_location'].replace(" ","").lower()
    departure_date = request.form['departure_date']

    trains = Railway.query.filter(
        func.replace(func.lower(Railway.from_location)," ","") == from_location,
        func.replace(func.lower(Railway.to_location)," ","") == to_location,
        func.date(Railway.departure_date) == departure_date
    ).all()
    return render_template('train_results.html',trains=trains)


# Show all trains on admin pannel
@app.route('/admin/trains',methods=['GET'])
def all_trains():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to acces this page.')
        return redirect(url_for('dashboard'))
    trains = Railway.query.all()
    return render_template('all_trains.html',trains=trains)


# for adding new train
@app.route('/admin/addRailway',methods=['GET','POST'])
def add_railway():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to acces this page.')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        train_name = request.form['train_name']
        from_location = request.form['from_location']
        to_location = request.form['to_location']
        departure_date = request.form['departure_date']
        seats = request.form['seats']
        price = request.form['price']
        new_train = Railway(train_name=train_name,from_location=from_location,to_location=to_location,departure_date=departure_date,price=price,seats=seats)
        db.session.add(new_train)
        db.session.commit()
        flash('Train is added')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_railway.html')

# for editing a train details
@app.route('/admin/edit_railway/<int:train_id>',methods=['GET','POST'])
def edit_railway(train_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to acces this page.')
        return redirect(url_for('dashboard'))
    railway = Railway.query.get(train_id)
    if request.method == 'POST':
        railway.train_name = request.form['train_name']
        railway.from_location = request.form['from_location']
        railway.to_location = request.form['to_location']
        railway.departure_date = request.form['departure_date']
        railway.price = request.form['price']
        railway.seats = request.form['seats']
        db.session.commit()
        flash('Train details updated')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_railway.html',railway=railway)


# for delete a train
@app.route('/admin/delete_train', methods=['POST'])
def delete_train():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to acces this page.')
        return redirect(url_for('dashboard'))
    train_id = request.form['train_id']
    train = Railway.query.get(train_id)

    db.session.delete(train)
    db.session.commit()
    flash('Train deleted successfully')
    return redirect(url_for('admin_dashboard'))


# This is for Bus
@app.route('/bus',methods=['GET','POST'])
def bus():


    return render_template('bus.html')

# for search Bus
@app.route('/bus/search_bus',methods=['POST'])
def search_bus():
    from_location = request.form['from_location'].replace(" ","").lower()
    to_location = request.form['to_location'].replace(" ","").lower()
    departure_date = request.form['departure_date']

    buses = Bus.query.filter(
        func.replace(func.lower(Bus.from_location)," ","")==from_location,
        func.replace(func.lower(Bus.to_location)," ","")==to_location,
        func.date(Bus.departure_date)==departure_date
    ).all()
    return render_template('bus_results.html',buses=buses)

# Show all bues on admin pannel
@app.route('/admin/buses',methods=['GET'])
def all_buses():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to acces this page.')
        return redirect(url_for('dashboard'))
    buses = Bus.query.all()
    return render_template('all_buses.html',buses=buses)


# for add a new bus
@app.route('/admin/addBus',methods=['GET','POST'])
def add_bus():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to acces this page.')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        bus_name = request.form['bus_name']
        from_location = request.form['from_location']
        to_location = request.form['to_location']
        departure_date = request.form['departure_date']
        seats = request.form['seats']
        price = request.form['price']
        new_bus = Bus(bus_name=bus_name,from_location=from_location,to_location=to_location,departure_date=departure_date,price=price,seats=seats)
        db.session.add(new_bus)
        db.session.commit()
        flash('Bus is added')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_bus.html')

# for editing bus details
@app.route('/admin/edit_bus/<int:bus_id>', methods=['GET', 'POST'])
def edit_bus(bus_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to access this page.')
        return redirect(url_for('dashboard'))

    bus = Bus.query.get(bus_id)

    if request.method == 'POST':
        bus.bus_name = request.form['bus_name']
        bus.from_location = request.form['from_location']
        bus.to_location = request.form['to_location']
        bus.departure_date = request.form['departure_date']
        bus.price = request.form['price']
        bus.seats = request.form['seats']
        db.session.commit()
        flash('Bus details updated successfully.')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_bus.html', bus=bus)


# for delete a bus
@app.route('/admin/delete_bus', methods=['POST'])
def delete_bus():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to acces this page.')
        return redirect(url_for('dashboard'))
    bus_id = request.form['bus_id']
    bus = Bus.query.get(bus_id)

    db.session.delete(bus)
    db.session.commit()
    flash('Bus deleted successfully')
    return redirect(url_for('admin_dashboard'))



# This is for Hotel
@app.route('/hotel',methods=['GET','POST'])
def hotel():

    return render_template('hotel.html')

# for search hotel
@app.route('/hotel/search_hotel', methods=['POST'])
def search_hotel():
    location = request.form['location'].replace(" ", "").lower()
    date = request.form['date']

    # Fetch hotels using the query
    hotels = Hotel.query.filter(
        func.replace(func.lower(Hotel.location), " ", "") == location,
        Hotel.date == date
    ).all()

    print(hotels)  # Debugging: Print hotels to ensure query results are fetched

    return render_template('hotel_results.html', hotels=hotels)


# Show all hotels on admin pannel
@app.route('/admin/hotels',methods=['GET'])
def all_hotels():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to acces this page.')
        return redirect(url_for('dashboard'))
    hotels = Hotel.query.all()
    return render_template('all_hotels.html',hotels=hotels)


# for adding new Hotel
@app.route('/admin/addHotel', methods=['GET', 'POST'])
def add_hotel():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to acces this page.')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        hotel_name = request.form['hotel_name']
        location = request.form['location']
        price_per_night = request.form['price_per_night']
        rooms = request.form['rooms']
        date = request.form['date']
        new_hotel = Hotel(hotel_name=hotel_name,location=location,price=price_per_night,date=date,room=rooms)
        db.session.add(new_hotel)
        db.session.commit()
        flash('Hotel is added')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_hotel.html')

# for editing hotel details
@app.route('/admin/edit_hotel/<int:hotel_id>',methods=['GET','POST'])
def edit_hotel(hotel_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to acces this page.')
        return redirect(url_for('dashboard'))
    hotel = Hotel.query.get(hotel_id)
    if request.method == 'POST':
        hotel.hotel_name = request.form['hotel_name']
        hotel.location = request.form['location']
        hotel.price = request.form['price_per_night']
        hotel.room = request.form['rooms']
        db.session.commit()
        flash('hotel details updated')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_hotel.html',hotel=hotel)

# for delete a Hotel
@app.route('/admin/delete_hotel', methods=['POST'])
def delete_hotel():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to acces this page.')
        return redirect(url_for('dashboard'))
    hotel_id = request.form['hotel_id']
    hotel = Flight.query.get(hotel_id)

    db.session.delete(hotel)
    db.session.commit()
    flash('Hotel deleted successfully')
    return redirect(url_for('admin_dashboard'))

# for passenger details page
@app.route('/passenger_details/<string:booking_type>/<int:transport_id>', methods=['GET'])
def passenger_details(booking_type, transport_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if booking_type == 'hotel':
        transport_details = Hotel.query.get(transport_id)
    elif booking_type == 'flight':
        transport_details = Flight.query.get(transport_id)
    elif booking_type == 'train':
        transport_details = Railway.query.get(transport_id)
    elif booking_type == 'bus':
        transport_details = Bus.query.get(transport_id)
    else:
        return "Invalid booking type", 400

    return render_template('passenger_details.html', booking_type=booking_type, transport_id=transport_id, transport_details=transport_details)


# for payment page
@app.route('/payment_page/<string:booking_type>/<int:transport_id>/<int:passenger_id>', methods=['GET'])
def payment_page(booking_type,transport_id,passenger_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Get hotel details (optional)
    # hotel = Hotel.query.get(transport_id)

    if booking_type == 'flight':
        price = Flight.query.get(transport_id)
    if booking_type == 'train':
        price = Railway.query.get(transport_id)
    if booking_type == 'bus':
        price = Bus.query.get(transport_id)
    if booking_type == 'hotel':
        price = Hotel.query.get(transport_id)
    amount = price.price
    return render_template('payment_page.html',booking_type=booking_type,transport_id=transport_id,passenger_id=passenger_id,amount=amount)

# for get price
def get_price(booking_type, transport_id):
    if booking_type == 'flight':
        return Flight.query.get(transport_id).price
    elif booking_type == 'train':
        return Railway.query.get(transport_id).price
    elif booking_type == 'bus':
        return Bus.query.get(transport_id).price
    elif booking_type == 'hotel':
        return Hotel.query.get(transport_id).price
    return 0  # Default if no price is found


# for processing booking
@app.route('/process_booking/<string:booking_type>/<int:transport_id>', methods=['POST'])
def process_booking(booking_type, transport_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Fetch the transport or hotel details based on booking type
    if booking_type == 'flight':
        transport = Flight.query.get(transport_id)
    elif booking_type == 'train':
        transport = Railway.query.get(transport_id)
    elif booking_type == 'bus':
        transport = Bus.query.get(transport_id)
    elif booking_type == 'hotel':
        transport = Hotel.query.get(transport_id)  # Assuming a Hotel model exists
    else:
        return "Invalid booking type", 400

    # Check availability
    if booking_type == 'hotel':
        if transport.room <= 0:  # Assuming 'rooms' indicates available hotel rooms
            flash("No rooms available for this booking.")
            return redirect(url_for('passenger_details', booking_type=booking_type, transport_id=transport_id))

        # Reduce available rooms by one
        transport.room -= 1
    else:
        if transport.seats <= 0:
            flash("No seats available for this booking.")
            return redirect(url_for('passenger_details', booking_type=booking_type, transport_id=transport_id))

        # Reduce available seats by one
        transport.seats -= 1

    # Commit availability changes
    db.session.commit()

    # Calculate the allotted seat or room number
    allotted_seat_or_room_number = transport.seats + 1 if booking_type != 'hotel' else transport.room + 1

    # Get passenger/guest details from the form
    passenger_name = request.form['passenger_name']
    age = request.form['age']
    phone_no = request.form['phone_no']
    gender = request.form['gender']
    user_id = session['user_id']

    # Create a new passenger/guest record
    new_passenger = Passenger(
        user_id=user_id,
        transport_id=transport_id,
        booking_type=booking_type,
        name=passenger_name,
        age=age,
        phone_no=phone_no,
        gender=gender,
        seat_number=allotted_seat_or_room_number  # Use the same field for seats or rooms
    )
    db.session.add(new_passenger)
    db.session.commit()

    return redirect(
        url_for('payment_page', booking_type=booking_type, transport_id=transport_id, passenger_id=new_passenger.id,
                seat_number=allotted_seat_or_room_number)
    )


# for payment
@app.route('/payment/<string:booking_type>/<int:transport_id>/<int:passenger_id>', methods=['POST'])
def process_payment(booking_type, transport_id, passenger_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    card_number = request.form['card_number']
    expiry_date = request.form['expiry_date']
    cvv = request.form['cvv']
    cardholder_name = request.form['cardholder_name']
    total_amount = float(request.form['total_amount'])

    if len(card_number) != 16 or len(cvv) != 3:
        flash('Invalid payment details. Please check your card information and try again.')
        return redirect(
            url_for('payment_page', booking_type=booking_type, transport_id=transport_id, passenger_id=passenger_id)
        )

    flash('Payment successful! Your booking is confirmed.')

    if card_number == '1234567890123456' and expiry_date == '10/2025' and cvv == '123' and cardholder_name == 'sandeep':
        new_booking = Booking(
            user_id=session['user_id'],
            booking_type=booking_type,
            transport_id=transport_id,
            amount=total_amount,
            passenger_id=passenger_id,
            status='confirmed'
        )
        db.session.add(new_booking)
        db.session.commit()

        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('payment_page'))


# for logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True,host='0.0.0.0', port=8000)
