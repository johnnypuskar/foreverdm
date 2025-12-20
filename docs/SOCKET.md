# Client/Server Socket Connection Structure

### `connect`

Initializes the socket IO connection and creates or joins a campaign instance as an active player character. Connection authorization parameters are passed through using the `auth` object.

|Parameter|Description|
|:---:|:---|
|`session_id`|The user's active session key retrieved from logging in.|
|`campaign_id`|The ID of the campaign to connect to.|

On connection, the `session_id` is used to verify if the user is in the `campaign_id` campaign. A response object is emitted through the socket connection after connecting. If this validation step fails, the socket connection is disconnected.

|Status|Response Event|Structure|
|:---:|:---:|:---|
|Success|`connect_response`|`{success: true}`|
|Failure|`error`|`{messsage: <error string>}`|

```
socket = io(URL, {
    auth: {
        session_key: "ABCD",
        campaign_id: "1234"
    }
})
```

### `get_view_data`

Returns all of the data for the current view and status of the `statblock_id` character.

|Parameter|Description|
|:---:|:---|
|`session_id`|The user's active session key retrieved from logging in.|
|`campaign_id`|The campaign for which to retrieve the view of.|
|`statblock_id`|The statblock for which to retrieve the view of.|

`statblock_id` must belong to the user associated with `session_id`, and both `statblock_id` and the `session_id` user must be a part of the `campaign_id` campaign.

|Status|Response Event|Structure|
|:---:|:---:|:---|
|Success|`set_instance_data`|`{view: <view act type>, data: {<view data>}}`|
|Failure|`error`|`{messsage: <error string>}`|

```
socket.emit('get_instance_data', {
    session_key: "ABDC",
    campaign_id: "1234",
    statblock_id: "abc"
});
```

### `send_command`

# **TODO**

### `disconnect`

Closes the socket IO connection and leaves campaign instance as active player character. Note that this does not remove your character from the world, simply flags them as inactive (i.e. not presently being controlled by their player).

#### **`No Parameters`**

#### **`No Response`**

```
socket.emit('disconnect')
```