return redirect('order_complete')





#func for placing an order

@login_required(login_url='login')
def place_order(request, total = 0, quantity=0):