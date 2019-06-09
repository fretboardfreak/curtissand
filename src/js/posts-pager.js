/*
 * posts-pager.js
 *
 * Version: 1.0
 */

import {Cookie} from "./cookie.js";


export class PostsPager {
  index = 0;
  metadata_url;
  metadata = {};
  items_per_page = 1;
  cookies = {};

  constructor(json_url){
    this.metadata_url = json_url;
    this.cookies['page'] = new Cookie('page', -1);
  }

  // Register click events for the pager controls
  static register_pager_events(instance) {
    $("#ppgr-next").click(function(){instance.next_page();});
    $("#ppgr-next-2").click(function(){instance.next_page();});
    $("#ppgr-prev").click(function(){instance.previous_page();});
    $("#ppgr-prev-2").click(function(){instance.previous_page();});
  }

  // Load the Posts Pager
  load () {
    $.ajax({
      url: this.metadata_url,
      data: '',
      type: 'GET',
      context: this,
      dataType: 'json',
      success: function(response){
        this.metadata = response;
        console.log('metadata loaded: ' + this.metadata.ids.length + ' post ids.');

        this.load_index_from_page_cookie();
        this.load_filter_elements();
        this.update();
      },
      error: function(error){
        console.log('Error loading pager data: '  + error);
      }
    });
  }

  page () {
    return Math.floor(this.index / this.items_per_page);
  }

  load_index_from_page_cookie () {
    var index_string = this.cookies['page'].get();
    if (index_string == "") {
      this.index = 0;
    } else {
      this.index = this.items_per_page * Number(index_string);
    }
  }

  set_page_cookie () {
    this.cookies['page'].set(this.page());
  }

  // Load filter elements from tags and category lists in metadata
  load_filter_elements () {
    console.log('PostsPager.load_filter_elements not implemented.');
  }

  // find a list of post ids based on the filter settings
  get_post_ids () {
    // TODO: incorporate filters here
    return this.metadata.ids.slice(this.index, this.index + this.items_per_page);
  }

  // render a post summary using html
  render_posts(dest_id, post_details) {
    console.log('rendering post: ' + dest_id);
    var post_html = '' +
      '<div class="container-fluid">' +
        '<div class="card bg-secondary w-80">' +
          '<div class="card-body">' +
            '<h5 class="card-title">' +
              '<a href="' + post_details.html + '" class="text-light">' + post_details.title + '</a>' +
            '</h5>' +
            '<h6 class="card-subtitle mb-2 text-muted">' +
              '<div class="row">' +
                '<div class="col">' +
                  '<span class="badge badge-pill badge-success mx-3">' + post_details.category + '</span>' +
                  '<span>' + post_details.date + '</span>' +
                '</div>' +
                '<div class="col">' +
                  '<span class="pl-3">Tags:&nbsp;</span>';
    for (var i = 0; i < post_details.tags.length; i += 1) {
      post_html += '<span class="badge badge-pill badge-info">' + post_details.tags[i] + '</span>';
    }
    post_html += '' +
                '</div>' +
              '</div>' +
            '</h6>' +
            '<p class="card-text">' + post_details.summary + '</p>' +
            '<div class="row">' +
              '<div class="col text-right">' +
                '<a href="' + post_details.html + '" class="card-link">Full Post</a>' +
              '</div>' +
              '<div class="col text-right">' +
                '<a href="./sources/' + post_details.source + '" class="card-link">Source</a>' +
              '</div>' +
            '</div>' +
          '</div>' +
        '</div>' +
      '</div>';
    $('#' + dest_id).html(post_html);
  }

  // Update the posts summary when page index or filter settings change
  update() {
    this.set_page_cookie();

    // get the list of post ids for the page
    var post_ids = this.get_post_ids();

    for (var i = 0; i < post_ids.length; i += 1) {
      // add empty div container for the post inside #ppgr-posts
      var div_html = '<div id="' + post_ids[i] + '" class="row my-2"></div>';
      if (i == 0) {
        $("#ppgr-posts").html(div_html);
      } else {
        $("#ppgr-posts").append(div_html);
      }

      this.render_posts(post_ids[i], this.metadata.posts[post_ids[i]]);
    }
  }

  // Move to the next page.
  next_page() {
    if (this.index + this.items_per_page <= this.metadata.ids.length - 1) {
      this.index = this.index + this.items_per_page;
      this.update();
    }
  }

  // Move to the previous page.
  previous_page() {
    if (this.index - this.items_per_page >= 0) {
      this.index = this.index - this.items_per_page;
      this.update();
    } else {
      this.index = 0;
      this.update();
    }
  }
}
