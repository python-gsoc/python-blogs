CKEDITOR.disableAutoInline = true;

		CKEDITOR.replace( 'editor1', {
			extraPlugins: 'image2',
			height: 600,
			contentsCss: [ '../../../contents.css', 'contents.css' ],
			extraAllowedContent: 'img[data-foo,data-bar]',

			filebrowserBrowseUrl: '/ckfinder/ckfinder.html',
			filebrowserImageBrowseUrl: '/ckfinder/ckfinder.html?Type=Images',
			filebrowserUploadUrl: '/ckfinder/core/connector/php/connector.php?command=QuickUpload&type=Files',
			filebrowserImageUploadUrl: '/ckfinder/core/connector/php/connector.php?command=QuickUpload&type=Images',
		} );

		CKEDITOR.inline( 'editor2', {
			extraPlugins: 'image2,sourcedialog'
		} );

		CKEDITOR.replace( 'editor3', {
			extraPlugins: 'image2,divarea',
			height: 600
		} );

		CKEDITOR.replace( 'editor4', {
			extraPlugins: 'image2',
			image2_alignClasses: [ 'align-left', 'align-center', 'align-right' ],
			contentsCss: [ '../../../contents.css', 'contents.css' ],
			height: 600
		} );

		CKCONSOLE.create( 'widget', { editor: 'editor1' } );
		CKCONSOLE.create( 'focus', { editor: 'editor1' } );
		CKCONSOLE.create( 'widget', { editor: 'editor2', folded: true } );
		CKCONSOLE.create( 'focus', { editor: 'editor2', folded: true } );
		CKCONSOLE.create( 'widget', { editor: 'editor3' } );
		CKCONSOLE.create( 'focus', { editor: 'editor3' } );
		CKCONSOLE.create( 'widget', { editor: 'editor4' } );
		CKCONSOLE.create( 'focus', { editor: 'editor4' } );

