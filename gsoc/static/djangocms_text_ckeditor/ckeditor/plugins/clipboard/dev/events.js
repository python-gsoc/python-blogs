( function()
{
	'use strict';

	var log = window.__log = function( title, msg ) {
		var msgEl = new CKEDITOR.dom.element( 'p' ),
			consoleEl = CKEDITOR.document.getById( 'console' ),
			time = new Date().toString().match( /\d\d:\d\d:\d\d/ )[ 0 ],
			format = function( tpl ) {
				return tpl.replace( /{time}/g, time ).replace( '{title}', title ).replace( '{msg}', msg || '' );
			};

		window.console && console.log && console.log( format( '[{time}] {title}: {msg}' ) );

		msg = ( msg || '' ).replace( /\r/g, '{\\r}' ).replace( /\n/g, '{\\n}' ).replace( /\t/g, '{\\t}' );
		msg = CKEDITOR.tools.htmlEncode( msg );
		msg = msg.replace( /\{(\\\w)\}/g, '<code class="specChar">$1</code>' );

		msgEl.setHtml( format( '<time datetime="{time}">{time}</time><span class="prompt">{title}</span> {msg}' ) );
		consoleEl.append( msgEl );
		consoleEl.$.scrollTop = consoleEl.$.scrollHeight;
		setTimeout( function() { msgEl.addClass( 'old' ); }, 250 );
	};

	var observe = function( editor, num ) {
		var p = 'EDITOR ' + num + ' > ';

		editor.on( 'paste', function( event ) {
			log( p + 'paste(prior:-1)', event.data.type + ' - "' + event.data.dataValue + '"' );
		}, null, null, -1 );
		editor.on( 'paste', function( event ) {
			log( p + 'paste(prior:10)', event.data.type + ' - "' + event.data.dataValue + '"' );
		} );
		editor.on( 'paste', function( event ) {
			log( p + 'paste(prior:999)', event.data.type + ' - "' + event.data.dataValue + '"' );
		}, null, null, 999 );
		editor.on( 'beforePaste', function( event ) {
			log( p + 'beforePaste', event.data.type );
		} );
		editor.on( 'beforePaste', function( event ) {
			log( p + 'beforePaste(prior:999)', event.data.type );
		}, null, null, 999 );
		editor.on( 'afterPaste', function( event ) {
			log( p + 'afterPaste' );
		} );
		editor.on( 'copy', function( event ) {
			log( p + 'copy' );
		} );
		editor.on( 'cut', function( event ) {
			log( p + 'cut' );
		} );
	};

	CKEDITOR.disableAutoInline = true;
	var config = {
			height: 120,
			toolbar: [ [ 'Source' ] ],
			allowedContent: true
		},
		editor1 = CKEDITOR.replace( 'editor1', config ),
		editor2 = CKEDITOR.replace( 'editor2', config ),
		editor3 = CKEDITOR.replace( 'editor3', config ),
		editor4 = CKEDITOR.replace( 'editor4', CKEDITOR.tools.extend( { forcePasteAsPlainText: true }, config ) ),
		editor5 = CKEDITOR.replace( 'editor5', CKEDITOR.tools.extend( { autoParagraph: false }, config ) ),
		editor6 = CKEDITOR.inline( document.getElementById( 'editor6' ), config );

	editor3.on( 'beforePaste', function( evt ) {
		evt.data.type = 'text';
	} );

	observe( editor1, 1 );
	observe( editor2, 2 );
	observe( editor3, 3 );
	observe( editor4, 4 );
	observe( editor5, 5 );
	observe( editor6, 6 );

})();
	
