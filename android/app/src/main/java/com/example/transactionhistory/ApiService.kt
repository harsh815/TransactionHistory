package com.example.transactionhistory

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface ApiService {
    @POST("api/sms")
    suspend fun sendSmsData(@Body request: SMSDataRequest): Response<Any>

    @GET("api/user/{userId}/summary")
    suspend fun getUserSummary(@Path("userId") userId: String): Response<UserSummary>
}