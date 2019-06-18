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
  items_per_page;
  cookies = {};

  constructor(json_url, items_per_page){
    this.metadata_url = json_url;
    this.items_per_page = items_per_page;
    this.cookies['page'] = new Cookie('page', -1);
    this.cookies['items_per_page'] = new Cookie('items_per_page', -1);
    this.cookies['category'] = new Cookie('category', -1);
  }

  // Register click events for the pager controls
  static register_pager_events(instance) {
    $("#apply-filter").click(function(){instance.apply_filter();})
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

        this.load_items_per_page_cookie();
        this.load_index_from_page_cookie();
        this.setup_page_chooser();
        this.setup_category_chooser();
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

  last_page () {
    return Math.floor(this.metadata.ids.length / this.items_per_page)
  }

  load_index_from_page_cookie () {
    var page = Number(this.cookies['page'].get());
    if (!Number.isInteger(page) || page < 0) {
      this.index = 0;
    } else if (page > this.last_page()){
      this.index = this.items_per_page * this.last_page()
    } else {
      this.index = this.items_per_page * page;
    }
  }

  load_items_per_page_cookie () {
    var items_per_page = this.cookies['items_per_page'].get();
    if (items_per_page == "") {
      items_per_page = 5;
    } else {
      items_per_page = Number(items_per_page);
    }
    if (items_per_page < 5) {
      items_per_page = 5;
    } else if (items_per_page > 50) {
      items_per_page = 50;
    }
    this.items_per_page = items_per_page;
  }

  // Load the page chooser form and set max page values
  setup_page_chooser () {
    var last_page_index = this.last_page();
    $('#page_chooser').attr('max', last_page_index);
    $('#page_chooser').val(this.page());
    $('#page_count').text(last_page_index);
  }

  // Load the category select statement with choices
  setup_category_chooser () {
    var chosen_category = this.cookies['category'].get();
    var choices_str = '';
    if (chosen_category == 'all') {
      choices_str += '<option value="all" selected>all</option>\n';
    } else {
      choices_str += '<option value="all">all</option>\n';
    }
    for (var i = 0; i < this.metadata.categories.length; i += 1){
      var category = this.metadata.categories[i];
      choices_str += '<option value="' + category;
      if (chosen_category == category) {
        choices_str += '" selected>';
      } else {
        choices_str += '">';
      }
      choices_str += category + '</option>\n';
    }
    $('#category_chooser').html(choices_str);
  }

  get_category_filter () {
    return $('#category_chooser').val();
  }

  // find a list of post ids based on the filter settings
  get_post_ids () {
    var category = this.get_category_filter();
    var post_ids = [];
    var count = 0;
    var max = this.index + this.items_per_page;

    if (category == 'all') {
      return this.metadata.ids.slice(this.index, this.index + this.items_per_page);
    }

    // only interested in posts that come after the set index
    var ids_slice = this.metadata.ids.slice(
      this.index, this.metadata.ids.length)

    for (var i = 0; i < ids_slice.length; i += 1) {
      var id = ids_slice[i];
      if (this.metadata.posts[id].category == category) {
        post_ids.push(id);
        count += 1;
      }
      if (count >= max) {
        break;
      }
    }

    return post_ids;
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
    this.cookies['page'].set(this.page());
    $("#page_chooser").val(this.page());

    this.cookies['items_per_page'].set(this.items_per_page);
    $("#items_per_page").val(this.items_per_page);

    this.cookies['category'].set(this.get_category_filter());

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

  // Apply changes to the filters and update.
  apply_filter () {
    console.log('Applying Filters...');

    // Items Per Page
    var items_per_page = Number($("#items_per_page").val());
    if (items_per_page < 5) {
      items_per_page = 5;
    } else if (items_per_page > 50) {
      items_per_page = 50;
    }
    this.items_per_page = items_per_page;

    // Page Chooser
    var page_val = Number($("#page_chooser").val());
    if (page_val < 0) {
      page_val = 0;
    } else if (page_val > this.last_page()) {
      page_val = this.last_page();
    }
    this.index = page_val * this.items_per_page;

    this.setup_page_chooser();
    this.update();
  }
}
