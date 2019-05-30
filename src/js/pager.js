/*
 * pager.js
 *
 * Version: 1.0
 */

export class Pager {
  index = 0;
  identifier;  // identifier for  Pager elements on html page
  json_url;
  media = [];
  load_cb; // callback used to format the contents of the page
  items_per_page = 1;

  constructor(identifier, json_url, load_cb){
    this.identifier = identifier;
    this.json_url = json_url;
    this.load_cb = load_cb;
  }

  // Register click events for the Next and Previous calls
  static register(instance) {
    $(".pgr-" + instance.identifier + "-next").click(function(){
      instance.next();
    });
    $(".pgr-" + instance.identifier + "-prev").click(function(){
      instance.previous();
    });
  }

  // Load the data from the server side JSON file
  load () {
    $.ajax({
      url: this.json_url,
      data: '',
      type: 'GET',
      context: this,
      dataType: 'json',
      success: function(response){
        this.media = response.data;
        console.log('Media is ' + this.media.length + ' items long.');
        this.update();
      },
      error: function(error){
        console.log('Error loading pager data: '  + error);
      }
    });
  }

  // Update the pager contents when a next or previous event is triggered.
  // The load_cb() callback is called with the pager content element and the
  // data for the next page from the JSON file. It is up to the load_cb()
  // callback to format the data and load them into the pager content element.
  update() {
    var page_contents = this.media.slice(this.index,
                                         this.index + this.items_per_page)
    this.load_cb($(".pgr-" + this.identifier), page_contents);

    console.log('pgr index is ' + this.index);
    if (this.index == 0) {
      var tag = $(".pgr-" + this.identifier + "-prev");
      tag.prop('disabled', true);
      tag.removeClass('text-light');
      tag.addClass('text-info');
    } else {
      var tag = $(".pgr-" + this.identifier + "-prev");
      tag.prop('disabled', false);
      tag.removeClass('text-info');
      tag.addClass('text-light');
    }
    if (this.index >= this.media.length - this.items_per_page) {
      var tag = $(".pgr-" + this.identifier + "-next");
      tag.prop('disabled', true);
      tag.removeClass('text-light');
      tag.addClass('text-info');
    } else {
      var tag = $(".pgr-" + this.identifier + "-next");
      tag.prop('disabled', false);
      tag.removeClass('text-info');
      tag.addClass('text-light');
    }
  }

  // Move to the next page.
  next() {
    if (this.index + this.items_per_page <= this.media.length - 1) {
      this.index = this.index + this.items_per_page;
      this.update();
    }
  }

  // Move to the previous page.
  previous() {
    if (this.index - this.items_per_page >= 0) {
      this.index = this.index - this.items_per_page;
      this.update();
    }
  }

}
