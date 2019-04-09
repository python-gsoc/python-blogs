if ( CKEDITOR.env.ie && CKEDITOR.env.version < 9 )
			CKEDITOR.tools.enableHtml5Elements( document );

		CKEDITOR.plugins.addExternal( 'simplebox', 'plugins/widget/dev/assets/simplebox/' );

		CKEDITOR.replace( 'editor1', {
			extraPlugins: 'simplebox,placeholder,image2',
			removePlugins: 'forms,bidi',
			contentsCss: [ '../../../contents.css', 'assets/simplebox/contents.css' ],
			height: 500
		} );

		CKEDITOR.inline( 'editor2', {
			extraPlugins: 'simplebox,placeholder,image2',
			removePlugins: 'forms,bidi'
		} );

		CKCONSOLE.create( 'widget', { editor: 'editor1' } );
		CKCONSOLE.create( 'focus', { editor: 'editor1' } );
		CKCONSOLE.create( 'widget', { editor: 'editor2', folded: true } );
		CKCONSOLE.create( 'focus', { editor: 'editor2', folded: true } );

