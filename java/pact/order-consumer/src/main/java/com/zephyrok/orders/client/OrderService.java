package com.zephyrok.orders.client;

import com.zephyrok.orders.model.Order;
import retrofit2.Call;
import retrofit2.http.GET;
import java.util.List;

public interface OrderService {
    @GET("orders")
    Call<List<Order>> getOrders();
}
