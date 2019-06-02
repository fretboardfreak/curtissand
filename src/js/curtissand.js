/*
 * Main JS Entrypoint
 *
 * Note:
 * Your customizations should be imported into this file.
 *
 */

import {PostsPager} from "./posts-pager.js";

// functions

export function load() {
  if(window.location.href.indexOf('about.html') > -1){
    console.log('loading about page.');
    $('#bio_content').load('./sources/about_body.html')
  } else if(window.location.href.indexOf('projects.html') > -1){
    console.log('loading projects page.');
    $('#projects').load('./sources/projects_body.html')
  } else if(window.location.href.indexOf('posts.html') > -1){
    console.log('loading posts page.');
    var posts_pager = new PostsPager('./sources/metadata.json');
    posts_pager.items_per_page = 10;
    PostsPager.register_pager_events(posts_pager);
    posts_pager.load();
    $('#apply-filter').click(function() {posts_pager.update();});
  }
  console.log('javascript loaded.');
}

// browser events

/* On DOM Ready Load the client. */
$(document).ready(function(){load();});
