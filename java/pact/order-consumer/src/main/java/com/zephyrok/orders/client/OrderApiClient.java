package com.zephyrok.orders.client;

import com.zephyrok.orders.model.Order;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.jackson.JacksonConverterFactory;

import java.io.IOException;
import java.util.List;

public class OrderApiClient {
    private final OrderService orderService;

    public OrderApiClient(String url) {
        Retrofit retrofit = new Retrofit.Builder()
                .baseUrl(url)
                .addConverterFactory(JacksonConverterFactory.create())
                .build();

        orderService = retrofit.create(OrderService.class);
    }

    public List<Order> fetchOrders() throws IOException {
        Response<List<Order>> response = orderService.getOrders().execute();
        return response.body();
    }
}
