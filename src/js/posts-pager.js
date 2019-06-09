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
    this.cookies['index'] = new Cookie('index', 1);
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

        this.get_index_from_cookie();
        this.load_filter_elements();
        this.update();
      },
      error: function(error){
        console.log('Error loading pager data: '  + error);
      }
    });
  }

  get_index_from_cookie () {
    var index_string = this.cookies['index'].get();
    if (index_string == "") {
      this.index = 0;
    } else {
      this.index = Number(index_string);
    }
  }

  set_index_cookie () {
    this.cookies['index'].set(this.index);
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

  // render a post using html in the following template
  // <div class="container-fluid">
  //   <div class="card bg-secondary w-80">
  //     <div class="card-body">
  //       <h5 class="card-title">Post Title</h5>
  //       <h6 class="card-subtitle mb-2 text-muted">
  //         <div class="row">
  //           <div class="col">
  //             <span class="badge badge-pill badge-success px-3">Category</span>
  //             2019-05-21 20:00
  //           </div>
  //           <div class="col">
  //             <span class="pl-3">Tags:&nbsp;</span>
  //             <span class="badge badge-pill badge-info">tag1</span>
  //           </div>
  //         </div>
  //       </h6>
  //       <p class="card-text">Post Summary</p>
  //       <div class="row">
  //         <div class="col text-right">
  //           <a href="#" class="card-link">Full Post</a>
  //         </div>
  //         <div class="col text-right">
  //           <a href="#" class="card-link">Source</a>
  //         </div>
  //       </div>
  //     </div>
  //   </div>
  // </div>
  render_posts(dest_id, post_details) {
    console.log('rendering post: ' + dest_id);
    var post_html = '<div class="container-fluid"><div class="card bg-secondary w-80"><div class="card-body">';
    post_html += '<h5 class="card-title">' + post_details.title + '</h5>';
    post_html += '<h6 class="card-subtitle mb-2 text-muted"><div class="row"><div class="col">'
    post_html += '<span class="badge badge-pill badge-success px-3">' + post_details.category + '</span>';
    post_html += '<span>' + post_details.date + '</span>';
    post_html += '</div><div class="col"><span class="pl-3">Tags:&nbsp;</span>';
    for (var i = 0; i < post_details.tags.length; i += 1) {
      post_html += '<span class="badge badge-pill badge-info">' + post_details.tags[i] + '</span>';
    }
    post_html += '</div></div></h6>';
    post_html += '<p class="card-text">' + post_details.summary + '</p>';
    post_html += '<div class="row"><div class="col text-right">';
    post_html += '<a href="' + post_details.html + '" class="card-link">Full Post</a>'; // TODO: update link to full post page
    post_html += '</div><div class="col text-right">';
    post_html += '<a href="./sources/' + post_details.source + '" class="card-link">Source</a>';
    post_html += '</div></div></div></div></div>';
    $('#' + dest_id).html(post_html);
  }

  // Update the posts summary when page index or filter settings change
  update() {
    this.set_index_cookie();

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
