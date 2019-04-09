CKEDITOR.replace( 'editor1', {
			extraPlugins: 'image2',
			height: 450,
			removePlugins: 'image,forms',
			contentsCss: [ '../../../contents.css', '../../image2/samples/contents.css' ]
		} );

		CKEDITOR.inline( 'editor2', {
			extraPlugins: 'image2',
			height: 450,
			removePlugins: 'image,forms'
		} );
