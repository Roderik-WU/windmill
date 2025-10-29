/*
 * Author: Windmill Labs, Inc
 * Copyright: Windmill Labs, Inc 2024
 * This file and its contents are licensed under the AGPLv3 License.
 * Please see the included NOTICE for copyright information and
 * LICENSE-AGPL for a copy of the license.
 */

use crate::{
    db::{ApiAuthed, DB},
    utils::require_super_admin,
};
use axum::{
    extract::{Extension, Path, Query},
    routing::{delete, get, post},
    Json, Router,
};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::value::RawValue;
use std::collections::HashMap;
use windmill_common::{
    error::{JsonResult, Result},
    jobs::JobPayload,
    mailbox::{MailboxType, MsgPayload},
    scripts::ScriptHash,
};
use windmill_queue::{push, PushArgs, PushIsolationLevel};

pub fn workspaced_service() -> Router {
    Router::new()
        .route("/list", get(list_mailbox_messages))
        .route("/:message_id", delete(delete_mailbox_message))
        .route("/:message_id/handle", post(handle_mailbox_message))
        .route("/bulk_delete", delete(bulk_delete_mailbox_messages))
}

#[derive(Serialize, Deserialize)]
pub struct MailboxMessage {
    pub message_id: i64,
    pub mailbox_id: Option<String>,
    pub workspace_id: String,
    pub r#type: MailboxType,
    pub created_at: DateTime<Utc>,
    pub payload: MsgPayload,
}

#[derive(Deserialize)]
pub struct ListMailboxQuery {
    pub mailbox_type: Option<MailboxType>,
    pub mailbox_id: Option<String>,
    pub message_id: Option<i64>,
    pub page: Option<u32>,
    pub per_page: Option<u32>,
}

#[derive(Deserialize)]
pub struct BulkDeleteRequest {
    pub message_ids: Vec<i64>,
}

async fn list_mailbox_messages(
    authed: ApiAuthed,
    Extension(db): Extension<DB>,
    Path(w_id): Path<String>,
    Query(query): Query<ListMailboxQuery>,
) -> JsonResult<Vec<MailboxMessage>> {
    require_super_admin(&db, &authed.email).await?;

    todo!()
}

async fn delete_mailbox_message(
    authed: ApiAuthed,
    Extension(db): Extension<DB>,
    Path((w_id, message_id)): Path<(String, i64)>,
) -> Result<String> {
    require_super_admin(&db, &authed.email).await?;

    todo!();

    Ok(format!("Deleted mailbox message {}", message_id))
}

async fn bulk_delete_mailbox_messages(
    authed: ApiAuthed,
    Extension(db): Extension<DB>,
    Path(w_id): Path<String>,
    Json(req): Json<BulkDeleteRequest>,
) -> Result<String> {
    require_super_admin(&db, &authed.email).await?;

    todo!();
}

async fn handle_mailbox_message(
    authed: ApiAuthed,
    Extension(db): Extension<DB>,
    Path((w_id, message_id)): Path<(String, i64)>,
) -> Result<String> {
    require_super_admin(&db, &authed.email).await?;

    todo!();
}
