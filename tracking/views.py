from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Document, DocumentAction, CustomUser
from .forms import DocumentCreateForm, DocumentActionForm
from django.utils import timezone




class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentCreateForm
    template_name = 'tracking/document_form.html'
    success_url = reverse_lazy('document-list')

    def form_valid(self, form):
        today = timezone.now().date()
        count_today = Document.objects.filter(created_at__date=today).count() + 1
        form.instance.created_by = self.request.user
        form.instance.current_handler = CustomUser.objects.get(role='B')
        form.instance.serial_number = count_today
        form.instance.sent_at = timezone.now()
        return super().form_valid(form)


class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'tracking/document_list.html'

    # def get_queryset(self):
    #     return Document.objects.filter(current_handler=self.request.user)
    def get_queryset(self):
        user = self.request.user
        if user.role == 'A':
            return Document.objects.filter(created_by=user)
        return Document.objects.filter(current_handler=user)


class DocumentActionView(LoginRequiredMixin, View):
   
    def get(self, request, pk):
        document = get_object_or_404(Document, pk=pk)
        form = DocumentActionForm()
        actions = document.actions.all().order_by('timestamp')
        return render(request, 'tracking/document_action.html', {
            'document': document,
            'form': form,
            'actions': actions
    })



    def post(self, request, pk):
        document = get_object_or_404(Document, pk=pk)
        form = DocumentActionForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            comment = form.cleaned_data['comment']
            user = request.user

            # Log the action
            DocumentAction.objects.create(
                document=document,
                user=user,
                action=action,
                comment=comment
            )

            order = ['A', 'B', 'C', 'D', 'E']
            current_idx = order.index(user.role)

            if action == 'APPROVE':
                # ✅ Set last approved by
                document.last_approved_by = user

                if user.role == 'E':
                    next_role = 'A'
                    document.status = 'COMPLETED'
                else:
                    next_role = order[current_idx + 1]
                    document.status = 'PENDING'

            else:  # REJECT
                next_role = 'A'
                document.status = 'REJECTED'
                document.last_approved_by = None  # Clear approval info

            # ✅ Set new handler
            document.current_handler = CustomUser.objects.get(role=next_role)
            document.save()

            return redirect('document-list')

        # If form is invalid, show previous actions too
        actions = document.actions.all().order_by('timestamp')
        return render(request, 'tracking/document_action.html', {
            'document': document,
            'form': form,
            'actions': actions
        })






# DASHBOARD VIEW
class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user

        user_docs = Document.objects.filter(created_by=user)
        actions = DocumentAction.objects.filter(user=user)

        # Count actions by type
        approve_count = actions.filter(action='APPROVE').count()
        reject_count = actions.filter(action='REJECT').count()

        stats = {
            'created': user_docs.count(),
            'PENDING': user_docs.filter(status='PENDING').count(),
            'APPROVED': user_docs.filter(status='APPROVED').count(),
            'REJECTED': user_docs.filter(status='REJECTED').count(),
            'COMPLETED': user_docs.filter(status='COMPLETED').count(),
            'actions_total': actions.count(),
            'approve_count': approve_count,
            'reject_count': reject_count,
        }

        return render(request, 'tracking/dashboard.html', {'stats': stats})
