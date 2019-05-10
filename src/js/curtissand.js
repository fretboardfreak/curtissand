/*
 * Main JS Entrypoint
 *
 * Note:
 * Your customizations should be imported into this file.
 *
 */

// functions

export function load() {
  console.log('javascript loaded.');
  $('#about').load('about.html')
}

// browser events

/* On DOM Ready Load the client. */
$(document).ready(function(){load();});
