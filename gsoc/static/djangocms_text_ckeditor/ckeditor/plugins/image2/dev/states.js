if ( CKEDITOR.env.ie && CKEDITOR.env.version < 9 )
			CKEDITOR.tools.enableHtml5Elements( document );

		var editor;

		// The instanceReady event is fired, when an instance of CKEditor has finished
		// its initialization.
		CKEDITOR.on( 'instanceReady', function( ev ) {
			editor = ev.editor;

			// Show this "on" button.
			document.getElementById( 'readOnlyOn' ).style.display = '';

			// Event fired when the readOnly property changes.
			editor.on( 'readOnly', function() {
				document.getElementById( 'readOnlyOn' ).style.display = this.readOnly ? 'none' : '';
				document.getElementById( 'readOnlyOff' ).style.display = this.readOnly ? '' : 'none';
			});
		});

		function toggleReadOnly( isReadOnly ) {
			// Change the read-only state of the editor.
			// http://docs.ckeditor.com/#!/api/CKEDITOR.editor-method-setReadOnly
			editor.setReadOnly( isReadOnly );
		}
