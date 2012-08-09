<script type="text/javascript">

	var _editor_url;
	var _editor_lang;

    // You must set _editor_url to the URL (including trailing slash) where
    // where AreaEdit is installed, it's highly recommended to use an absolute URL
    //  eg: _editor_url = "/path/to/areaedit/";
    // You may try a relative URL if you wish]
    //  eg: _editor_url = "../";

    // for this example we're using a little regular expression to find the absolute path.
	 // so that this demo will work "out of the box".
	 // 
	 // However, this means if you change the name of this page or the use this code in 
	 // your own page you will need to set _editor_url below. 
	 //
	 // Please note that the value of _editor_url must contain a trailing slash.

    _editor_url  = "{HTMLEditorURL}";

    _editor_lang = "en";      // And the language we need to use in the editor.

  </script>

  <!-- Load up the actual editor core -->
  <script type="text/javascript" src="{HTMLEditorURL}htmlarea.js"></script>

  <script type="text/javascript">




   var areaedit_editors = null;
   var areaedit_init    = null;
   var areaedit_config  = null;
   var areaedit_plugins = null;

	//startupDDT._ddt( "simple_example.html", "71", "Setting up areaedit_init()" );

	// --------------------------------------------------------------------------------

	/**
	* sample initialization function 
	*
	* this is called from the body onload handler below. It sets up the configurations
	* and builds the editor.
	*/
	areaedit_init = function()
		{

		// This is a workaround for a bug in MSIE that sometimes produces
		// "Operation Aborted" errors. The error comes from the fact that
		// MSIE will /sometimes/ call the onload handler before the DOM
		// heirarchy is completely built. 
		//
		// So we do not run this function until the page has completely 
		// loaded if we are MSIE.

		if ( HTMLArea.is_ie && document.readyState != "complete" )
			{
			setTimeout( function() { areaedit_init()}, 50 );
			return false;
			}
		
		//startupDDT._ddt( "simple_example.html", "76", "areaedit_init called from window.onload handler for simple_example.php" );

		// Initialize the HTMLArea class. (Used to be at the bottom of htmlarea.js)
		HTMLArea.init();

      /** STEP 1 ***************************************************************
       * First, what are the plugins you will be using in the editors on this
       * page.  List all the plugins you will need, even if not all the editors
       * will use all the plugins.
       ************************************************************************/

		// a minmal list of plugins.

      var areaedit_plugins_minimal = 
      [

			'ContextMenu',
			 'CharacterMap',
			 'SuperClean',
			 //'HtmlTidy',
			 'InsertAnchor',
			 'EnterParagraphs',
			'DynamicCSS',
			//'EditTag', * does not work
			'ListType',
			'FindReplace',
			//'Forms',
			'InsertSmiley',
			//'InsertPagebreak',
			'TableOperations',
			//'Template', * does not work
			'UnFormat',
			'Stylist',
			 //'FormOperations',
			'BackgroundImage',
			'QuickTag',

      ];

      // This loads the plugins. We're using a very minimal list
		// here.
		//
		// loadPlugins causes the plugin .js files (in this case content-menu.js,
		// linker.js and image-manager.js) in the "background". The second parameter
		// here is a callback that gets invoked while we're waiting for things to load,
		// which in this case just causes us to loop back to here. Once everything 
		// is loaded loadPlugins() returns true and we can continue on.

	   //startupDDT._ddt( "simple_example.html", "92", "calling HTMLArea.loadplugins()" );

      if ( !HTMLArea.loadPlugins( areaedit_plugins_minimal, areaedit_init)) 
			{
			return;
			}

      /** STEP 2 ***************************************************************
       * Now, what are the names of the textareas you will be turning into
       * editors? For this example we're only loading 1 editor.
       ************************************************************************/

      areaedit_editors = 
      [
			'messhtml2'
      ];

      /** STEP 3 ***************************************************************
       * We create a default configuration to be used by all the editors.
       * If you wish to configure some of the editors differently this will be
       * done in step 4.
       *
       * If you want to modify the default config you might do something like this.
       *
       *   areaedit_config = new HTMLArea.Config();
       *   areaedit_config.width  = 640;
       *   areaedit_config.height = 420;
       *
       *************************************************************************/

  	    //startupDDT._ddt( "simple_example.html", "119", "calling HTMLArea.Config()" );

       areaedit_config = new HTMLArea.Config();

      /** STEP 3 ***************************************************************
       * We first create editors for the textareas.
       *
       * You can do this in two ways, either
       *
       *   areaedit_editors   = HTMLArea.makeEditors(areaedit_editors, areaedit_config, areaedit_plugins);
       *
       * if you want all the editor objects to use the same set of plugins, OR;
       *
       *   areaedit_editors = HTMLArea.makeEditors(areaedit_editors, areaedit_config);
       *   areaedit_editors['myTextArea'].registerPlugins(['Stylist','FullScreen']);
       *   areaedit_editors['anotherOne'].registerPlugins(['CSS','SuperClean']);
       *
       * if you want to use a different set of plugins for one or more of the
       * editors.
       ************************************************************************/

      //startupDDT._ddt( "simple_example.html", "140", "calling HTMLArea.makeEditors()" );

      areaedit_editors   = HTMLArea.makeEditors(areaedit_editors, areaedit_config, areaedit_plugins_minimal);

      /** STEP 4 ***************************************************************
       * If you want to change the configuration variables of any of the
       * editors,  this is the place to do that, for example you might want to
       * change the width and height of one of the editors, like this...
       *
       *   areaedit_editors.myTextArea.config.width  = 640;
       *   areaedit_editors.myTextArea.config.height = 480;
       *
       ************************************************************************/

       areaedit_editors.messhtml2.config.width  = 700;
       areaedit_editors.messhtml2.config.height = 350;

      /** STEP 5 ***************************************************************
       * Finally we "start" the editors, this turns the textareas into
       * AreaEdit editors.
       ************************************************************************/

      //startupDDT._ddt( "simple_example.html", "160", "calling HTMLArea.startEditors()" );

      HTMLArea.startEditors(areaedit_editors);

    	}  // end of areaedit_init()

	/**
	* javascript submit handler.
	*
	* this shows how to create a javascript submit 
	* button that works with the htmleditor.
	*/

	var submitHandler = function(formname) 
		{
	   var form = document.getElementById(formname);

		// in order for the submit to work both of these methods have to be
		// called.

	   form.onsubmit(); 
		form.submit();
		}

	</script>

