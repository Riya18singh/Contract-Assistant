from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ContractUploadForm
from .models import Contract,ChatMessage
from .rag_utils import process_contract, ask_question


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

    if request.method == 'POST':
        question = request.POST.get('question')
        result = ask_question(question, contract_id)

        ChatMessage.objects.create(
            contract=contract,
            question=question,
            answer=result['answer'],
            source=result['source'],
        )

        return redirect('chat', contract_id=contract.id)

    messages = contract.messages.all()

    return render(request, 'contracts/chat.html', {
        'contract': contract,
        'messages': messages,
    })
@login_required
def contract_list(request):
    contracts = Contract.objects.filter(owner=request.user).order_by('-uploaded_at')
    return render(request, 'contracts/list.html', {'contracts': contracts})
        