# Disable repos which cause errors for 'apt update'

When a repository becomes inaccessible or when a repo GPG key expires
'apt update' fails loudly and asks for administator to intervene.

This is not good in automated scenarios where the error may be automatically
fixed down the line (e.g. repo key update may have already been scheduled).
This script will attempt to update apt cache and if any of the configured
repos gets in the way - the script will just disable the offending repo.

Exit code 200 will indicate that the run was not exactly clean, but at
least all further 'apt update' calls will be successful and will not prevent
automated system healing.


## License and copyright

Copyright 2022 Vitaly Potyarkin

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
