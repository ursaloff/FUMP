var nbsp = 160;// non-breaking space char
var node_text = 3;// DOM text node-type
var emptyString = /^\s*$/ ;
var global_valfield;// retain valfield for timer thread
function trim(str)
{
  return str.replace(/^\s+|\s+$/g, '');
}
function setFocusDelayed()
{
  global_valfield.focus();
}
function setfocus(valfield)
{
  // save valfield in global variable so value retained when routine exits
  global_valfield = valfield;
  setTimeout( 'setFocusDelayed()', 100 );
}
function msg(fld,     // id of element to display message in
             msgtype, // class to give element ("warn" or "error")
             message) // string to display
{
  var dispmessage;
  if (emptyString.test(message)) 
    dispmessage = String.fromCharCode(nbsp);
  else  
    //dispmessage = message;
    dispmessage = '!';
  var elem = document.getElementById(fld);
  elem.firstChild.nodeValue = dispmessage;  
//  elem.className = msgtype;   // set the CSS class to adjust appearance of message
}
var proceed = 2;  
function commonCheck    (valfield,   // element to be validated
                         infofield,  // id of element to receive info/error msg
                         required)   // true if required
{
  if (!document.getElementById) 
    return true;  // not available on this browser - leave validation to the server
  var elem = document.getElementById(infofield);
  if (!elem.firstChild) return true;  // not available on this browser 
  if (elem.firstChild.nodeType != node_text) return true;  // infofield is wrong type of node  

  if (emptyString.test(valfield.value)) {
    if (required) {
      msg (infofield, "error", "ERROR: required");  
      setfocus(valfield);
      return false;
    }
    else {
      msg (infofield, "warn", "");   // OK
      return true;  
    }
  }
  return proceed;
}
function validatePresent(valfield,   // element to be validated
                         infofield ) // id of element to receive info/error msg
{
  var stat = commonCheck (valfield, infofield, true);
  if (stat != proceed) return stat;

  msg (infofield, "warn", "");  
  return true;
}
function validateEmail  (valfield,   // element to be validated
                         infofield,  // id of element to receive info/error msg
                         required)   // true if required
{
  var stat = commonCheck (valfield, infofield, required);
  if (stat != proceed) return stat;

  var tfld = trim(valfield.value);  // value of field with whitespace trimmed off
  var email = /^[^@]+@[^@.]+\.[^@]*\w\w$/  ;
  if (!email.test(tfld)) {
    msg (infofield, "error", "ERROR: not a valid e-mail address");
    setfocus(valfield);
    return false;
  }
  var email2 = /^[A-Za-z][\w.-]+@\w[\w.-]+\.[\w.-]*[A-Za-z][A-Za-z]$/  ;
  if (!email2.test(tfld)) 
    msg (infofield, "warn", "Unusual e-mail address - check if correct");
  else
    msg (infofield, "warn", "");
  return true;
}
function validateOnSubmit() {
    var elem;
    var errs=0;
    if (!validateEmail  (document.forms.subscribeform.email, 'validateemailmess', true)) errs += 1; 
    if (!validatePresent(document.forms.subscribeform.name,  'validatenamemess'))        errs += 1; 
    {validate_additional}
    if (errs>1)  alert('There are fields which need correction before sending');
    if (errs==1) alert('There is a field which needs correction before sending');
    return (errs==0);
};

