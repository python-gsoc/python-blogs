CKEDITOR.on( 'instanceCreated', function( ev ){
			var editor = ev.editor;

			// Listen for the "pluginsLoaded" event, so we are sure that the
			// "dialog" plugin has been loaded and we are able to do our
			// customizations.
			editor.on( 'pluginsLoaded', function() {

				// If our custom dialog has not been registered, do that now.
				if ( !CKEDITOR.dialog.exists( 'myDialog' ) ) {
					// We need to do the following trick to find out the dialog
					// definition file URL path. In the real world, you would simply
					// point to an absolute path directly, like "/mydir/mydialog.js".
					var href = document.location.href.split( '/' );
					href.pop();
					href.push( 'assets/my_dialog.js' );
					href = href.join( '/' );

					// Finally, register the dialog.
					CKEDITOR.dialog.add( 'myDialog', href );
				}

				// Register the command used to open the dialog.
				editor.addCommand( 'myDialogCmd', new CKEDITOR.dialogCommand( 'myDialog' ) );

				// Add the a custom toolbar buttons, which fires the above
				// command..
				editor.ui.add( 'MyButton', CKEDITOR.UI_BUTTON, {
					label: 'My Dialog',
					command: 'myDialogCmd'
				});
			});
		});

		// When opening a dialog, its "definition" is created for it, for
		// each editor instance. The "dialogDefinition" event is then
		// fired. We should use this event to make customizations to the
		// definition of existing dialogs.
		CKEDITOR.on( 'dialogDefinition', function( ev ) {
			// Take the dialog name and its definition from the event data.
			var dialogName = ev.data.name;
			var dialogDefinition = ev.data.definition;

			// Check if the definition is from the dialog we're
			// interested on (the "Link" dialog).
			if ( dialogName == 'myDialog' && ev.editor.name == 'editor2' ) {
				// Get a reference to the "Link Info" tab.
				var infoTab = dialogDefinition.getContents( 'tab1' );

				// Add a new text field to the "tab1" tab page.
				infoTab.add( {
					type: 'text',
					label: 'My Custom Field',
					id: 'customField',
					'default': 'Sample!',
					validate: function() {
						if ( ( /\d/ ).test( this.getValue() ) )
							return 'My Custom Field must not contain digits';
					}
				});

				// Remove the "select1" field from the "tab1" tab.
				infoTab.remove( 'select1' );

				// Set the default value for "input1" field.
				var input1 = infoTab.get( 'input1' );
				input1[ 'default' ] = 'www.example.com';

				// Remove the "tab2" tab page.
				dialogDefinition.removeContents( 'tab2' );

				// Add a new tab to the "Link" dialog.
				dialogDefinition.addContents( {
					id: 'customTab',
					label: 'My Tab',
					accessKey: 'M',
					elements: [
						{
							id: 'myField1',
							type: 'text',
							label: 'My Text Field'
						},
						{
							id: 'myField2',
							type: 'text',
							label: 'Another Text Field'
						}
					]
				});

				// Provide the focus handler to start initial focus in "customField" field.
				dialogDefinition.onFocus = function() {
					var urlField = this.getContentElement( 'tab1', 'customField' );
					urlField.select();
				};
			}
		});

		var config = {
			extraPlugins: 'dialog',
			toolbar: [ [ 'MyButton' ] ]
		};

