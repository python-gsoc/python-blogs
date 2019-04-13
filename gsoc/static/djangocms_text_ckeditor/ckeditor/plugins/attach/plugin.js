/*
  Author - Sahil Batla
  Contact - sahilbathla1@gmail.com
  Description - This plugins provides a basic iframe to upload attachments
  Configs while using in editor -
  1) AutoClose -  To auto close dialog on upload (autoClose: true)
  2) Callback on attachment upload - onAttachmentUpload: function() {}
  3) validateSize - Validate size of file before upload (validateSize: 30) i.e 30mb limit
*/
attachmentUploader = {
  uploadButton: null,
  editor: null,
  uploadEventBinded: false,
  uploadingContainer: null,
  statusMessageContainer :null,
  uploadingSource: CKEDITOR.plugins.getPath('attach') + 'uploading.gif',
  autoClose: false,
  validateSize: 0,
  setStatusMessageContainer: function(_this) {
    this.statusMessageContainer = _this.getElement();
  },
  setUploadingContainer: function(_this) {
    this.uploadingContainer = _this.getElement()
  },
  setuploadButton: function(_this) {
    this.uploadButton = $(_this.getInputElement().$.children[0]);
  },
  getFileField: function() {
    return $($('body').find('iframe.cke_dialog_ui_input_file:visible').contents().find('input[type="file"]'));
  },
  getResultantHTML: function() {
    return $($('body').find('iframe.cke_dialog_ui_input_file:visible').contents().find('body')).html();
  },
  bindUploadEvent: function() {
    //Handle iframe redirect
    var uploadHandler = function() {
      if (attachmentUploader.uploadButton.text() == 'Uploading..') {
        //Provide onAttachmentUpload Callback after upload
        //Define this function in CKEDITOR config
        if (attachmentUploader.editor.config.onAttachmentUpload) {
          attachmentUploader.editor.config.onAttachmentUpload(attachmentUploader.getResultantHTML());
        }
        attachmentUploader.uploadButton.text('Uploaded');
        attachmentUploader.statusMessageContainer.setText('File Upload Successful!!');
        attachmentUploader.statusMessageContainer.show();
        attachmentUploader.uploadingContainer.hide();
        if (attachmentUploader.autoClose) {
          CKEDITOR.dialog.getCurrent().hide();
        }
      }
    }
    $('body').find('iframe.cke_dialog_ui_input_file').load(uploadHandler);
    attachmentUploader.uploadEventBinded = true;
  }
}

CKEDITOR.dialog.add( 'abbrDialog', function( editor ) {
  return {
    title: 'Upload Attachments',
    minWidth: 400,
    minHeight: 200,

    contents: [
      {
        id: 'Upload',
        filebrowser: 'uploadButton',
        hidden: true,
        elements: [
          {
            type: 'html',
            html: 'Please upload a single file, zip and upload multiple files if required'
          },
          {
            type: 'file',
            id: 'attachment',
            inputStyle: 'outline: 0',
            style: 'height:40px',
            size: 38,
          },
          {
            type: 'fileButton',
            id: 'uploadButton',
            filebrowser: 'info:txtUrl',
            label: editor.lang.image.btnUpload,
            'for': [ 'Upload', 'attachment' ],
            onClick: function() {
              var attachment = attachmentUploader.getFileField();
              if (attachment.val()) {
                if ( attachmentUploader.validateSize > 0 && attachment[0].files[0].size > attachmentUploader.validateSize * 1000000 ) {
                  alert('File Size Limit is ' + attachmentUploader.validateSize + 'mb');
                  attachment.val('');
                } else {
                  attachmentUploader.uploadButton.text('Uploading..').parent('a').hide();
                  attachmentUploader.uploadingContainer.show();
                }
              } else {
                alert('Please select a file first');
              }
            },
            onLoad: function() {
              attachmentUploader.setuploadButton(this);
            }
          },
          {
            type: 'html',
            html: '<img class="uploading-img" src="' + attachmentUploader.uploadingSource + '"></img',
            style: 'margin-left:35%',
            hidden: true,
            onLoad: function() {
              attachmentUploader.setUploadingContainer(this);
            }
          },
          {
            type: 'html',
            html: '<div class="status-message"></div>',
            style: 'margin-left:32%;  color: green',
            hidden: true,
            onLoad: function() {
              attachmentUploader.setStatusMessageContainer(this);
            }
          }
        ]
      },
    ],
    onOk: function(event) {
      if(attachmentUploader.uploadButton.text() != 'Uploaded') {
        if(!confirm('Please make sure you send files to server or else upload will be cancelled!!')) {
          event.preventDefault();
        }
      }
    },
    onShow: function() {
      //Remove Focus & fix height
      var fileField = attachmentUploader.getFileField().css('outline', 0);
      $('body').find('iframe.cke_dialog_ui_input_file').css('height', '36px');

      if (attachmentUploader.uploadButton) {
        attachmentUploader.uploadButton.text('Upload attachment').parent('a').show();
      }
      //bindUploadEvent only if not binded before
      if (!attachmentUploader.uploadEventBinded) {
        attachmentUploader.bindUploadEvent();
      }
      attachmentUploader.statusMessageContainer.setText('');
      attachmentUploader.statusMessageContainer.hide();

      //setCustomConfiguration
      attachmentUploader.autoClose = attachmentUploader.editor.config.autoCloseUpload || false;
      attachmentUploader.validateSize = attachmentUploader.editor.config.validateSize || 0;
    }
  }
});

CKEDITOR.plugins.add('attach',
{
  init: function (editor) {
    attachmentUploader.editor = editor;
    var pluginName = 'attach';
    editor.ui.addButton('Attachments',
    {
      label: 'Attach files',
      command: 'OpenWindow',
      icon: CKEDITOR.plugins.getPath('attach') + 'attach.png'
    });
    var cmd = editor.addCommand('OpenWindow', new CKEDITOR.dialogCommand('abbrDialog'));
  }
});