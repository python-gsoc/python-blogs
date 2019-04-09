CKEDITOR.addCss(
			'.cke_editable * { outline: 1px solid #BCEBFF }'
		);

		function callback() {
			var helpers = CKEDITOR.plugins.lineutils;
			var liner = new helpers.liner( this );
			var locator = new helpers.locator( this );
			var finder = new helpers.finder( this, {
				lookups: {
					'is block and first child': function( el ) {
						if ( el.is( CKEDITOR.dtd.$listItem ) )
							return;

						if ( el.is( CKEDITOR.dtd.$block ) )
							return CKEDITOR.LINEUTILS_BEFORE | CKEDITOR.LINEUTILS_AFTER;
					}
				}
			} ).start( function( relations, x, y ) {
				locator.locate( relations );

				var locations = locator.locations,
					uid, type;

				liner.prepare( relations, locations );

				for ( uid in locations ) {
					for ( type in locations[ uid ] )
						liner.placeLine( { uid: uid, type: type } );
				}

				liner.cleanup();
			} );
		}

		CKEDITOR.disableAutoInline = true;

		CKEDITOR.replace( 'editor1', {
			extraPlugins: 'lineutils',
			height: 450,
			removePlugins: 'magicline',
			allowedContent: true,
			contentsCss: [ '../../../contents.css' ],
			on: {
				contentDom: callback
			}
		} );

		CKEDITOR.inline( 'editor2', {
			extraPlugins: 'lineutils',
			removePlugins: 'magicline',
			allowedContent: true,
			contentsCss: [ '../../../contents.css' ],
			on: {
				contentDom: callback
			}
		} );

		CKEDITOR.inline( 'editor3', {
			extraPlugins: 'lineutils',
			removePlugins: 'magicline',
			allowedContent: true,
			contentsCss: [ '../../../contents.css' ],
			on: {
				contentDom: callback
			}
		} );

		CKEDITOR.replace( 'editor4', {
			extraPlugins: 'lineutils',
			removePlugins: 'magicline',
			allowedContent: true,
			contentsCss: [ '../../../contents.css' ],
			on: {
				contentDom: callback
			}
		} );


