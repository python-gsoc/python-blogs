CKEDITOR.disableAutoInline = true;

		function hideshow( id ) {
			var element = CKEDITOR.document.getById( id );

			if( element.getStyle( 'display' ) == 'none' )
				element.show();
			else
				element.hide();
		}

		CKEDITOR.replace( 'classic' );
		CKEDITOR.inline( 'inline' );

		CKCONSOLE.addEventPanel( 'dragstart', [ '$', 'target', 'dataTransfer' ] );
		CKCONSOLE.addEventPanel( 'dragend', [ '$', 'target', 'dataTransfer' ]	);
		CKCONSOLE.addEventPanel( 'drop',
			[ '$', 'target', 'dataTransfer', 'dragRange', 'dropRange' ] );

		CKCONSOLE.create( 'dragstart', { editor: 'classic' } );
		CKCONSOLE.create( 'drop', { editor: 'classic' } );
		CKCONSOLE.create( 'paste', { editor: 'classic' } );
		CKCONSOLE.create( 'dragend', { editor: 'classic' } );

		CKCONSOLE.create( 'dragstart', { editor: 'inline' } );
		CKCONSOLE.create( 'drop', { editor: 'inline' } );
		CKCONSOLE.create( 'paste', { editor: 'inline' } );
		CKCONSOLE.create( 'dragend', { editor: 'inline' } );
