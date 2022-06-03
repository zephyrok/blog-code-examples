package com.zephyrok.orders;

import au.com.dius.pact.consumer.MockServer;
import au.com.dius.pact.consumer.dsl.PactDslWithProvider;
import au.com.dius.pact.consumer.junit5.PactConsumerTestExt;
import au.com.dius.pact.consumer.junit5.PactTestFor;
import au.com.dius.pact.core.model.V4Pact;
import au.com.dius.pact.core.model.annotations.Pact;
import com.zephyrok.orders.client.OrderApiClient;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;

import java.io.IOException;
import java.util.Map;

import static au.com.dius.pact.consumer.dsl.LambdaDsl.*;

@ExtendWith(PactConsumerTestExt.class)
public class OrderApiClientPactTest {
    @Pact(provider = "order_provider", consumer = "order_consumer")
    public V4Pact listOfOrdersPact(PactDslWithProvider builder) {
        return builder
                .given("there are orders")
                .uponReceiving("a request for orders")
                .path("/orders")
                .method("GET")
                .willRespondWith()
                .status(200)
                .headers(Map.of("Content-Type", "application/json"))
                .body(newJsonArrayMinLike(1, a -> a.object(o -> {
                    o.id("id");
                    o.eachLike("items", i -> {
                        i.stringType("name");
                        i.numberType("quantity");
                        i.numberType("value");
                    });
                })).build())
                .toPact(V4Pact.class);
    }

    @Pact(provider = "order_provider", consumer = "order_consumer")
    public V4Pact noOrdersPact(PactDslWithProvider builder) {
        return builder
                .given("there are no orders")
                .uponReceiving("a request for orders")
                .path("/orders")
                .method("GET")
                .willRespondWith()
                .status(200)
                .headers(Map.of("Content-Type", "application/json"))
                .body("[]")
                .toPact(V4Pact.class);
    }

    @Test
    @PactTestFor(pactMethod = "listOfOrdersPact")
    void getListOfOrders(MockServer mockServer) throws IOException {
        var client = new OrderApiClient(mockServer.getUrl());
        var orders = client.fetchOrders();
        Assertions.assertNotNull(orders);
        Assertions.assertFalse(orders.isEmpty());
        Assertions.assertNotNull(orders.get(0).getItems());
        Assertions.assertFalse(orders.get(0).getItems().isEmpty());
    }

    @Test
    @PactTestFor(pactMethod = "noOrdersPact")
    void getEmptyListOfOrders(MockServer mockServer) throws IOException {
        var client = new OrderApiClient(mockServer.getUrl());
        var orders = client.fetchOrders();
        Assertions.assertNotNull(orders);
        Assertions.assertTrue(orders.isEmpty());
    }
}
