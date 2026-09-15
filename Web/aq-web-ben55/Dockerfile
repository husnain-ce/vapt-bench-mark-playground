FROM php:8.3.4-apache

RUN a2enmod rewrite

RUN sed -i 's/AllowOverride None/AllowOverride All/' /etc/apache2/apache2.conf

COPY src/ /var/www/html

COPY flag.txt /flag.txt

RUN chmod -R 555 /var/www/html && \
    chown -R root:root /var/www/html && \
    chown root:root /flag.txt && \
    mv /flag.txt "/flag-$(head /dev/urandom | sha256sum | head -c 24).txt"

EXPOSE 80

USER www-data