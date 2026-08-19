from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ContractUploadForm
from .rag_utils import process_contract
from django.shortcuts import get_object_or_404
from .models import Contract
from .rag_utils import ask_question


@login_required
def upload_contract(request):
    if request.method == 'POST':
        form = ContractUploadForm(request.POST, request.FILES)
        if form.is_valid():
            contract = form.save(commit=False)
            contract.owner = request.user
            contract.save()

            # Now that the file is saved, run our RAG pipeline on it
            process_contract(contract.file.path, contract.id)

            return redirect('chat', contract_id=contract.id)
    else:
        form = ContractUploadForm()

    return render(request, 'contracts/upload.html', {'form': form})

@login_required
def chat_with_contract(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id, owner=request.user)
    answer = None
    question = None

    if request.method == 'POST':
        question = request.POST.get('question')
        answer = ask_question(question, contract_id)

    return render(request, 'contracts/chat.html', {
        'contract': contract,
        'question': question,
        'answer': answer,
    })
