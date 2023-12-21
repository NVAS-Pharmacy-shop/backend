from io import BytesIO

import qrcode
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from company import models


def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save the image to a BytesIO buffer
    buffer = BytesIO()
    img.save(buffer)
    return buffer.getvalue()

def send_reservation_email(reservation_id, recipient_email):
    # Generate QR code
    reservation_info = models.EquipmentReservation.objects.get(id=reservation_id)

    qr_code_data = (f'\tReservation ID: {reservation_info.id}\n'
                    f'\tUser: {reservation_info.user.email}\n'
                    f'\tDate: {reservation_info.date}\n')

    for reserved_equipment in reservation_info.reserved_equipment.all():
        qr_code_data += f'\t{reserved_equipment.equipment.name} x {reserved_equipment.quantity}\n'


    qr_code_image = generate_qr_code(qr_code_data)




    # Create an email message with the QR code attached
    subject = 'Reservation Confirmation'
    message = f'Hi {reservation_info.user.first_name},\n\n' \
                f'Your reservation has been confirmed.\n\n' \
                f'Here is your reservation information:\n'
    message += qr_code_data
    message += '\n\nThank you for using our service.\n\n' \
                'Regards,\n' \
                'The NVASHealth Solutions Team'
    email = EmailMessage(
        subject,
        message,
        to=[recipient_email],
    )


    # Attach the QR code image
    email.attach('reservation_qr_code.png', qr_code_image, 'image/png')

    # Send the email
    email.send()
