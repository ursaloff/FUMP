function clearhtmltags(str, allowed_tags) {
    var key = '', allowed = false;
    var matches = [];
    var allowed_array = [];
    var allowed_tag = '';
    var i = 0;
    var k = '';
    var html = '';
    var replacer = function(search, replace, str) {
        return str.split(search).join(replace);
    };
    if (allowed_tags) {
        allowed_array = allowed_tags.match(/([a-zA-Z]+)/gi);
    }
    str += '';
    matches = str.match(/(<\/?[\S][^>]*>)/gi);
    for (key in matches) {
        if (isNaN(key)) {
            // IE7 Hack
            continue;
        }
        html = matches[key].toString();
        allowed = false;
        for (k in allowed_array) {
            allowed_tag = allowed_array[k];
            i = -1;
            if (i != 0) { i = html.toLowerCase().indexOf('<'+allowed_tag+'>');}
            if (i != 0) { i = html.toLowerCase().indexOf('<'+allowed_tag+' ');}
            if (i != 0) { i = html.toLowerCase().indexOf('</'+allowed_tag)   ;}
            if (i == 0) {
                allowed = true;
                break;
            }
        }
        if (!allowed) {
           if(html.indexOf("<br>") != -1 || html.indexOf("<br/>") != -1 || html.indexOf("<br />") != -1 || html.indexOf("<p>") != -1 || html.indexOf("</p>") != -1) {
              str = replacer(html, "\n", str);
           } else {
              str = replacer(html, "", str);
           }
             
        }        
    }
    str = str.replace(/&nbsp;/gi,' ');
    str = str.replace("\n\n","\n");
    return str;
}

function copyhtmltotext() {
   if(document.messform.type.selectedIndex != 2) {
      document.messform.type.selectedIndex = 2;
      ProcessPageVisability();
   }
   document.getElementById('mess').value = clearhtmltags(document.getElementById('messhtml').value);
}

var last_open_img;

function show_img_preview(img_id) {
   if(document.getElementById('image_prev_div_'+ img_id)) {
      document.getElementById('image_prev_div_'+ img_id).style.display = 'inline';
      last_open_img = 'image_prev_div_'+ img_id;
   }
}

function hide_img_preview() {
   if(document.getElementById(last_open_img)) {
      document.getElementById(last_open_img).style.display = 'none';
   }
}