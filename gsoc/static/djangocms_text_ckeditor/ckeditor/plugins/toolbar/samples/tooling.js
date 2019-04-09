(function() {
	'use strict';

	var buttonsNames;

	CKEDITOR.config.extraPlugins = 'toolbar';

	CKEDITOR.on( 'instanceReady', function( evt ) {
		var editor = evt.editor,
			editorCurrent = editor.name == 'editorCurrent',
			defaultToolbar = !( editor.config.toolbar || editor.config.toolbarGroups || editor.config.removeButtons ),
			pre = CKEDITOR.document.getById( editor.name + 'Cfg' ),
			output = '';

		if ( editorCurrent ) {
			// If default toolbar configuration has been modified, show "current toolbar" section.
			if ( !defaultToolbar )
				CKEDITOR.document.getById( 'currentToolbar' ).show();
			else
				return;
		}

		if ( !buttonsNames )
			buttonsNames = createButtonsNamesHash( editor.ui.items );

		// Toolbar isn't set explicitly, so it was created automatically from toolbarGroups.
		if ( !editor.config.toolbar ) {
			output +=
				'// Toolbar configuration generated automatically by the editor based on config.toolbarGroups.\n' +
				dumpToolbarConfiguration( editor ) +
				'\n\n' +
				'// Toolbar groups configuration.\n' +
				dumpToolbarConfiguration( editor, true )
		}
		// Toolbar groups doesn't count in this case - print only toolbar.
		else {
			output += '// Toolbar configuration.\n' +
				dumpToolbarConfiguration( editor );
		}

		// Recreate to avoid old IE from loosing whitespaces on filling <pre> content.
		var preOutput = pre.getOuterHtml().replace( /(?=<\/)/, output );
		CKEDITOR.dom.element.createFromHtml( preOutput ).replace( pre );
	} );

	CKEDITOR.replace( 'editorCurrent', { height: 100 } );
	CKEDITOR.replace( 'editorFull', {
		// Reset toolbar settings, so full toolbar will be generated automatically.
		toolbar: null,
		toolbarGroups: null,
		removeButtons: null,
		height: 100
	} );

	function dumpToolbarConfiguration( editor, printGroups ) {
		var output = [],
			toolbar = editor.toolbar;

		for ( var i = 0; i < toolbar.length; ++i ) {
			var group = dumpToolbarGroup( toolbar[ i ], printGroups );
			if ( group )
				output.push( group );
		}

		return 'config.toolbar' + ( printGroups ? 'Groups' : '' ) + ' = [\n\t' + output.join( ',\n\t' ) + '\n];';
	}

	function dumpToolbarGroup( group, printGroups ) {
		var output = [];

		if ( typeof group == 'string' )
			return '\'' + group + '\'';
		if ( CKEDITOR.tools.isArray( group ) )
			return dumpToolbarItems( group );
		// Skip group when printing entire toolbar configuration and there are no items in this group.
		if ( !printGroups && !group.items )
			return;

		if ( group.name )
			output.push( 'name: \'' + group.name + '\'' );

		if ( group.groups )
			output.push( 'groups: ' + dumpToolbarItems( group.groups ) );

		if ( !printGroups )
			output.push( 'items: ' + dumpToolbarItems( group.items ) );

		return '{ ' + output.join( ', ' ) + ' }';
	}

	function dumpToolbarItems( items ) {
		if ( typeof items == 'string' )
			return '\'' + items + '\'';

		var names = [],
			i, item;

		for ( var i = 0; i < items.length; ++i ) {
			item = items[ i ];
			if ( typeof item == 'string' )
				names.push( item );
			else {
				if ( item.type == CKEDITOR.UI_SEPARATOR )
					names.push( '-' );
				else
					names.push( buttonsNames[ item.name ] );
			}
		}

		return '[ \'' + names.join( '\', \'' ) + '\' ]';
	}

	// Creates { 'lowercased': 'LowerCased' } buttons names hash.
	function createButtonsNamesHash( items ) {
		var hash = {},
			name;

		for ( name in items ) {
			hash[ items[ name ].name ] = name;
		}

		return hash;
	}

})();
