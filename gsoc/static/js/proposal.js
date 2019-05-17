function cancelProposalUpload() {
  axios.get('/cancel_proposal_upload/').then(
    function(resp) {
        inPageInfo("Proposal upload canceled.");
        setProposalUploadingStatus(false);
    }
  )
}
function setProposalUploadingStatus(status) {
  const button = document.querySelector("#upload-proposal-button");
  if(status) {
    button.innerHTML = 'Uploading...Please wait.';
    button.onclick = null;
  } else {
    button.innerHTML = 'Confirm';
    button.onclick = beforeUpload;
  }
}
function inPageInfo(text, isAlert=true) {
  const boxTag = document.querySelector('#infoBox');
  const boxText = document.querySelector('#infoBoxText');
  boxText.innerHTML = text;
  if(isAlert)boxTag.className = 'alert';
  else boxTag.className = 'info';

  boxTag.style.display = 'inline-block';
}
document.getElementById('proposalFileInput').onchange = function(){
  hideInfoBox();
  const fileInput = document.getElementById('proposalFileInput');
  const file = fileInput.files[0];
  const fileSizeTooLarge = file && file.size > 20 * 1024 * 1024;
  const fileWrongFormat = file && !file.name.endsWith(".pdf");
  if (fileSizeTooLarge){
    inPageInfo(`Sorry, your proposal file is too large<br>
Please keep the file smaller than 20MB.`);
    fileInput.value = '';
  }
  if (fileWrongFormat){
    inPageInfo(`Sorry, the file you just chose doesn't seem to be a pdf file.`);
    fileInput.value = '';
  }

};
function hideInfoBox() {
  const boxTag = document.querySelector('#infoBox');
  boxTag.style.display = 'none';
}
function beforeUpload() {
  const offlineCancel = function(){
    inPageInfo("Proposal upload canceled.")
    };
  const infoText = 'Please make sure there is no private data in your pdf file. Confirm?'
  inPageInfo(infoText, false);
  showInfoBoxBtns(uploadProposal, offlineCancel)
}
function hideInfoBoxBtns() {
  const btn1 = document.querySelector('#infoBtn1');
  const btn2 = document.querySelector('#infoBtn2');
  btn1.onclick = null;
  btn2.onclick = null;
  btn1.style.display = 'none';
  btn2.style.display = 'none';
}
function showInfoBoxBtns(callback1, callback2) {
  const btn1 = document.querySelector('#infoBtn1');
  const btn2 = document.querySelector('#infoBtn2');
  btn1.onclick = function(){hideInfoBoxBtns(); hideInfoBox(); callback1()};
  btn2.onclick = function(){hideInfoBoxBtns(); hideInfoBox(); callback2()};
  btn1.style.display = 'inline';
  btn2.style.display = 'inline';
}
function onFindPrivateData(text) {
  const successCallback = function() {
    inPageInfo("Upload succeeded! Please refresh to get rid of the GIANT banner!",false);
    setProposalUploadingStatus(false);
  };
  showInfoBoxBtns(successCallback, cancelProposalUpload);
  inPageInfo(text, true);
}
function uploadProposal() {
  hideInfoBoxBtns();
  setProposalUploadingStatus(true);
  const uploadForm = document.querySelector('#upload-proposal-form');
  axios.post(
    '/upload-proposal/',
    new FormData(uploadForm),
  )
    .then(function(resp) {
      if(!resp.data['file_type_valid']) {
        inPageInfo("Your file doesn't seem to be a pdf file. Please check again!");
        setProposalUploadingStatus(false);
        return
      }
      if(!resp.data['file_not_too_large']) {
        inPageInfo("Your file is larger than 20MB. Please make it smaller!");
        setProposalUploadingStatus(false);
        return
      }
      const privateData = resp.data['private_data'];
      if(privateData["emails"].length > 0 ||
      privateData["possible_phone_numbers"].length > 0 ||
      privateData["locations"].length > 0) {
        let confirmText = "We seemed to have found private data in your pdf file. WE DO NOT RECOMEND UPLOADING A PDF WITH PHONE NUMBERS, PHYSICAL ADDRESS, OR EMAIL ADDRESSES AS THIS WILL BE SHOWN PUBLICALLY ON THE INTERNET. Are you sure to proceed?";
        if (privateData['emails'].length > 0)
        confirmText += `<br> Email addresses: ${privateData['emails'].toString()}`
        if(privateData['possible_phone_numbers'].length > 0)
        confirmText += `<br> Possible phone numbers: ${privateData['possible_phone_numbers'].toString()}`
        if(privateData['locations'].length > 0)
        confirmText += `<br> Locations: ${privateData['locations'].toString()}`
        onFindPrivateData(confirmText);
        return
      }
      setProposalUploadingStatus(false);
      inPageInfo('Proposal upload succeeded! Please refresh to get rid of the GIANT banner!', false);
    })
    .catch(function(err) {
      setProposalUploadingStatus(false);
      console.log(err);
    })
}
