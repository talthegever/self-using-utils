package com.phoneagent.app.action

sealed class ExecutionResult(val message: String) {
    class Success(message: String) : ExecutionResult(message)
    class Failure(message: String) : ExecutionResult(message)
}
