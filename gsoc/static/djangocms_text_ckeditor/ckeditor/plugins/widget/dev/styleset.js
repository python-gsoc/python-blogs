if ( CKEDITOR.env.ie && CKEDITOR.env.version < 9 )
			CKEDITOR.tools.enableHtml5Elements( document );

		CKEDITOR.disableAutoInline = true;

		var stylesSet = [
			{ name: 'Medium border', type: 'widget', widget: 'image', attributes: { 'class': 'mediumBorder' } },
			{ name: 'Thick border', type: 'widget', widget: 'image', attributes: { 'class': 'thickBorder' } },
			{ name: 'So important', type: 'widget', widget: 'image', attributes: { 'class': 'important soMuch' } },

			{ name: 'Red marker', type: 'widget', widget: 'placeholder', attributes: { 'class': 'redMarker' } },
			{ name: 'Invisible Placeholder', type: 'widget', widget: 'placeholder', attributes: { 'class': 'invisible' } },

			{ name: 'Invisible Mathjax', type: 'widget', widget: 'mathjax', attributes: { 'class': 'invisible' } }
		];

		CKEDITOR.replace( 'editor1', {
			extraPlugins: 'placeholder,image2,mathjax',
			contentsCss: [ '../../../contents.css', 'assets/contents.css' ],
			stylesSet: stylesSet,
			height: 300
		} );

		CKEDITOR.inline( 'editor2', {
			extraPlugins: 'placeholder,image2,mathjax',
			stylesSet: stylesSet,
			height: 300
		} );

