package com.example.transactionhistory

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

interface ApiService {
    @POST("api/sms")
    suspend fun sendSmsData(@Body request: SMSDataRequest): Response<JobResponse>

    @GET("api/job/{jobId}")
    suspend fun getJobStatus(@Path("jobId") jobId: String): Response<JobStatus>

    @GET("api/user/{userId}/summary")
    suspend fun getUserSummary(
        @Path("userId") userId: String,
        @Query("timeframe") timeframe: String
    ): Response<UserSummary>
}