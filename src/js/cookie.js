/*
 * cookie.js
 *
 * get and set functions borrowed from:
 * https://www.w3schools.com/js/js_cookies.asp
 *
 * Version: 1.0
 */

// Cookie class stores a text based key value pair cookie on the document
export class Cookie {
  name;
  expiry_days;

  constructor(name, expiry_days) {
    this.name = name;
    this.expiry_days = expiry_days;
  }

  // Set the value of the cookie
  set (value) {
    var date = new Date();
    if (this.expiry_days >= 0) {
      date.setTime(date.getTime() + (this.expiry_days * 24 * 60 * 60 * 1000));
      var expires = "expires=" + date.toUTCString(); + ";";
    } else {
      var expires = "";
    }
    document.cookie = this.name + "=" + value + ";" + expires + "path=/";
  }

  // Retrieve the value of the cookie string
  get () {
    var name_token = this.name + "=";
    var cookie_parts = document.cookie.split(';');
    for(var i = 0; i < cookie_parts.length; i++) {
      var part = cookie_parts[i];
      while (part.charAt(0) == ' ') {
        part = part.substring(1);
      }
      if (part.indexOf(name_token) == 0) {
        return part.substring(name_token.length, part.length);
      }
    }
    return "";  // this cookie key not found in document cookies string
  }
}
